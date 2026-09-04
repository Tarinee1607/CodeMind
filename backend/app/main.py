import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from .db import engine, Base, get_db
from . import models, schemas, auth, ingest, embed, answer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to create all tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")
except Exception as e:
    logger.error(f"Failed to create database tables: {e}")

app = FastAPI(title="CodeMind API")

# Allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev. Restrict in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def health_check():
    return {"status": "ok", "message": "pong"}

@app.post("/signup", response_model=schemas.Token)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user_data.password)
    new_user = models.User(email=user_data.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = auth.create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/repos")
def add_repo(repo_data: schemas.RepoCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Create Repo entry
    new_repo = models.Repo(user_id=current_user.id, github_url=repo_data.github_url)
    db.add(new_repo)
    db.commit()
    db.refresh(new_repo)
    
    # Ingest and embed
    try:
        chunks = ingest.ingest_repo(repo_data.github_url)
        embed.embed_and_store(chunks, str(new_repo.id))
        return {"status": "success", "repo_id": new_repo.id, "chunks_processed": len(chunks)}
    except Exception as e:
        db.delete(new_repo)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to process repository: {str(e)}")

@app.get("/repos")
def list_repos(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    repos = db.query(models.Repo).filter(models.Repo.user_id == current_user.id).all()
    return [{"id": r.id, "github_url": r.github_url, "created_at": r.created_at} for r in repos]

@app.get("/repos/{repo_id}/tree")
def get_repo_tree_endpoint(repo_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    repo = db.query(models.Repo).filter(models.Repo.id == repo_id, models.Repo.user_id == current_user.id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found or unauthorized")
    
    try:
        tree = ingest.get_repo_tree(repo.github_url)
        return {"repo_name": repo.github_url.split("/")[-1].replace(".git", ""), "tree": tree}
    except Exception as e:
        logger.error(f"Failed to get repo tree: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to build repository tree: {str(e)}")

@app.get("/repos/{repo_id}/er-diagram")
def get_repo_er_diagram(repo_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    repo = db.query(models.Repo).filter(models.Repo.id == repo_id, models.Repo.user_id == current_user.id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found or unauthorized")
    
    try:
        schema_code = ingest.extract_schema_files(repo.github_url)
        if not schema_code.strip():
            return {"mermaid": "erDiagram\n    NO_DATABASE_SCHEMA_FOUND { string message }"}
            
        mermaid_code = answer.generate_er_diagram(schema_code)
        return {"mermaid": mermaid_code}
    except Exception as e:
        logger.error(f"Failed to generate ER diagram: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate ER diagram: {str(e)}")

@app.post("/ask")
def ask_question(request: schemas.AskRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    repo = db.query(models.Repo).filter(models.Repo.id == request.repo_id, models.Repo.user_id == current_user.id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found or unauthorized")
    retrieved = embed.retrieve(request.question, str(repo.id))
    
    if not retrieved:
        generated_answer = "No relevant code found to answer the question. This might happen if the repository is empty, lacks supported code files, or doesn't match your query."
        retrieved_meta = []
        response_sources = []
    else:
        generated_answer = answer.generate_answer(request.question, retrieved)
        retrieved_meta = [
            {
                "file": chunk["metadata"]["file_path"],
                "lines": f"{chunk['metadata']['start_line']}-{chunk['metadata']['end_line']}",
                "name": chunk["metadata"]["name"]
            }
            for chunk in retrieved
        ]
        response_sources = [
            {**meta, "code_text": chunk.get("document", "")}
            for meta, chunk in zip(retrieved_meta, retrieved)
        ]
    
    import json
    chat_entry = models.ChatHistory(
        user_id=current_user.id,
        repo_id=repo.id,
        question=request.question,
        answer=generated_answer,
        retrieved_files=json.dumps(retrieved_meta)
    )
    db.add(chat_entry)
    db.commit()
    
    return {"answer": generated_answer, "sources": response_sources}

@app.get("/chat_history/{repo_id}")
def get_chat_history(repo_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    history = db.query(models.ChatHistory).filter(models.ChatHistory.repo_id == repo_id, models.ChatHistory.user_id == current_user.id).order_by(models.ChatHistory.timestamp.desc()).all()
    return [{"question": h.question, "answer": h.answer, "sources": h.retrieved_files, "timestamp": h.timestamp} for h in history]

@app.get("/history")
def get_all_history(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    import json
    # Join ChatHistory with Repo to get the repo's github_url
    results = db.query(models.ChatHistory, models.Repo.github_url).join(
        models.Repo, models.ChatHistory.repo_id == models.Repo.id
    ).filter(
        models.ChatHistory.user_id == current_user.id
    ).order_by(models.ChatHistory.timestamp.desc()).all()
    
    formatted = []
    for h, github_url in results:
        try:
            sources = json.loads(h.retrieved_files) if h.retrieved_files else []
            # handle legacy comma-separated string if present
            if isinstance(sources, str):
                raise ValueError()
        except Exception:
            sources = [{"file": s, "lines": "", "name": ""} for s in h.retrieved_files.split(",")] if h.retrieved_files else []
            
        formatted.append({
            "repo_name": github_url.split("/")[-1] if github_url else "Unknown",
            "question": h.question,
            "answer": h.answer,
            "sources": sources,
            "timestamp": h.timestamp
        })
        
    return formatted

import ollama

def generate_answer(question, retrieved_chunks):
    # Build prompt context
    context = ""
    for i, chunk in enumerate(retrieved_chunks):
        meta = chunk["metadata"]
        context += f"--- Chunk {i+1} ---\n"
        context += f"File: {meta['file_path']}\n"
        context += f"Name: {meta['name']}\n"
        context += f"Lines: {meta['start_line']} to {meta['end_line']}\n"
        code_str = chunk['document']
        if len(code_str) > 1000:
            code_str = code_str[:1000] + "\n... (truncated)"
        context += f"Code:\n{code_str}\n\n"
        
    prompt = f"""You are a helpful coding assistant. Use the provided code chunks to answer the user's question.
You MUST explicitly reference the file name and exact line numbers from the provided chunks in your answer.
Do not guess line numbers or file names; only use the ones explicitly given in the context.

Context Code Chunks:
{context}

Question: {question}

Answer:"""

    try:
        response = ollama.generate(model='phi3', prompt=prompt)
        return response.get('response', 'No response generated.')
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"
        
import re

def generate_er_diagram(schema_code):
    mermaid_lines = ["erDiagram"]
    
    # Simple heuristic regex for SQL CREATE TABLE
    table_pattern = re.compile(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\((.*?)\);", re.IGNORECASE | re.DOTALL)
    for match in table_pattern.finditer(schema_code):
        table_name = match.group(1)
        columns_text = match.group(2)
        
        mermaid_lines.append(f"    {table_name} {{")
        
        # parse columns roughly
        lines = columns_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.upper().startswith("PRIMARY KEY") or line.upper().startswith("FOREIGN KEY") or line.upper().startswith("KEY") or line.upper().startswith("CONSTRAINT"):
                continue
            
            parts = line.split()
            if len(parts) >= 2:
                col_name = parts[0].replace('`', '').replace('"', '')
                col_type = parts[1].replace(',', '').split('(')[0]
                mermaid_lines.append(f"        {col_type} {col_name}")
                
        mermaid_lines.append("    }")
        
    if len(mermaid_lines) > 1:
        return "\n".join(mermaid_lines)
        
    # If no SQL tables found, fallback to extremely simple LLM prompt with very short context
    # Truncate aggressively to 30000 chars 
    short_schema = schema_code[:30000]
    prompt = f"""You are an expert database architect. Extract the database schema from the following code and output a valid Mermaid 'erDiagram'.
RULES:
1. ONLY output the mermaid code block. No explanations.
2. Start the code block with ```mermaid and end with ```
3. Syntax: TABLE_NAME {{ type column_name }}

Code:
{short_schema}
"""
    try:
        response = ollama.generate(model='phi3', prompt=prompt)
        text = response.get('response', '')
        if "```mermaid" in text:
            start = text.find("```mermaid") + 10
            end = text.find("```", start)
            if end != -1: return text[start:end].strip()
        return text.strip()
    except Exception as e:
        return f"erDiagram\n    ERROR {{ string message \"{str(e)}\" }}"

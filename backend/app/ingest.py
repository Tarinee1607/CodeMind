import os
import tempfile
import shutil

# Configure GitPython to use local MinGit
git_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mingit", "cmd", "git.exe")
os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = git_path

from git import Repo
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_java as tsjava
import tree_sitter_cpp as tscpp
import tree_sitter_dart as tsdart
import tree_sitter_php as tsphp
import tree_sitter_html as tshtml
import tree_sitter_css as tscss
from tree_sitter import Language, Parser

def get_parser(extension):
    if extension == ".py":
        lang = Language(tspython.language())
    elif extension in [".js", ".jsx"]:
        lang = Language(tsjavascript.language())
    elif extension == ".java":
        lang = Language(tsjava.language())
    elif extension in [".cpp", ".cc", ".cxx", ".hpp", ".h"]:
        lang = Language(tscpp.language())
    elif extension == ".dart":
        lang = Language(tsdart.language())
    elif extension == ".php":
        lang = Language(tsphp.language_php())
    elif extension == ".html":
        lang = Language(tshtml.language())
    elif extension == ".css":
        lang = Language(tscss.language())
    else:
        return None
    parser = Parser(lang)
    return parser

def extract_nodes(node, code_bytes, ext, chunks, file_path):
    types_to_extract_py = {"function_definition": "function", "class_definition": "class"}
    types_to_extract_js = {
        "function_declaration": "function",
        "class_declaration": "class",
        "method_definition": "function"
    }
    types_to_extract_java = {
        "method_declaration": "function",
        "class_declaration": "class"
    }
    types_to_extract_cpp = {
        "function_definition": "function",
        "class_specifier": "class",
        "struct_specifier": "class"
    }
    types_to_extract_dart = {
        "class_definition": "class"
    }
    types_to_extract_php = {
        "function_definition": "function",
        "method_declaration": "function",
        "class_declaration": "class"
    }
    types_to_extract_html = {
        "element": "html_element"
    }
    types_to_extract_css = {
        "rule_set": "css_rule"
    }

    if ext == ".py" and node.type in types_to_extract_py:
        name_node = None
        for child in node.children:
            if child.type == "identifier":
                name_node = child
                break
        name = code_bytes[name_node.start_byte:name_node.end_byte].decode('utf8') if name_node else "unknown"
        chunks.append({
            "file_path": file_path,
            "chunk_type": types_to_extract_py[node.type],
            "name": name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "code_text": code_bytes[node.start_byte:node.end_byte].decode('utf8', errors='replace')
        })
    elif ext in [".js", ".jsx"]:
        if node.type in types_to_extract_js:
            name_node = None
            for child in node.children:
                if child.type in ["identifier", "property_identifier"]:
                    name_node = child
                    break
            name = code_bytes[name_node.start_byte:name_node.end_byte].decode('utf8') if name_node else "unknown"
            chunks.append({
                "file_path": file_path,
                "chunk_type": types_to_extract_js[node.type],
                "name": name,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "code_text": code_bytes[node.start_byte:node.end_byte].decode('utf8', errors='replace')
            })
        elif node.type in ["lexical_declaration", "variable_declaration"]:
            for child in node.children:
                if child.type == "variable_declarator":
                    has_arrow = False
                    name_node = None
                    for gc in child.children:
                        if gc.type == "identifier":
                            name_node = gc
                        elif gc.type == "arrow_function":
                            has_arrow = True
                    if has_arrow:
                        name = code_bytes[name_node.start_byte:name_node.end_byte].decode('utf8') if name_node else "unknown"
                        chunks.append({
                            "file_path": file_path,
                            "chunk_type": "function",
                            "name": name,
                            "start_line": node.start_point[0] + 1,
                            "end_line": node.end_point[0] + 1,
                            "code_text": code_bytes[node.start_byte:node.end_byte].decode('utf8', errors='replace')
                        })
    elif ext == ".java" and node.type in types_to_extract_java:
        name_node = None
        for child in node.children:
            if child.type == "identifier":
                name_node = child
                break
        name = code_bytes[name_node.start_byte:name_node.end_byte].decode('utf8') if name_node else "unknown"
        chunks.append({
            "file_path": file_path,
            "chunk_type": types_to_extract_java[node.type],
            "name": name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "code_text": code_bytes[node.start_byte:node.end_byte].decode('utf8', errors='replace')
        })
    elif ext in [".cpp", ".cc", ".cxx", ".hpp", ".h"] and node.type in types_to_extract_cpp:
        name_node = None
        # In C++, finding the name is trickier (e.g., function_declarator -> identifier)
        # We will do a generic depth-limited search for the first identifier
        def find_identifier(n):
            if n.type in ["identifier", "field_identifier", "type_identifier"]:
                return n
            for c in n.children:
                res = find_identifier(c)
                if res: return res
            return None
            
        name_node = find_identifier(node)
        name = code_bytes[name_node.start_byte:name_node.end_byte].decode('utf8') if name_node else "unknown"
        chunks.append({
            "file_path": file_path,
            "chunk_type": types_to_extract_cpp[node.type],
            "name": name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "code_text": code_bytes[node.start_byte:node.end_byte].decode('utf8', errors='replace')
        })
    elif ext == ".dart" and node.type in types_to_extract_dart:
        name_node = None
        for child in node.children:
            if child.type == "identifier":
                name_node = child
                break
        name = code_bytes[name_node.start_byte:name_node.end_byte].decode('utf8') if name_node else "unknown"
        chunks.append({
            "file_path": file_path,
            "chunk_type": types_to_extract_dart[node.type],
            "name": name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "code_text": code_bytes[node.start_byte:node.end_byte].decode('utf8', errors='replace')
        })
    elif ext == ".php" and node.type in types_to_extract_php:
        name_node = None
        for child in node.children:
            if child.type == "name" or child.type == "identifier":
                name_node = child
                break
        name = code_bytes[name_node.start_byte:name_node.end_byte].decode('utf8') if name_node else "unknown"
        chunks.append({
            "file_path": file_path,
            "chunk_type": types_to_extract_php[node.type],
            "name": name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "code_text": code_bytes[node.start_byte:node.end_byte].decode('utf8', errors='replace')
        })
    elif ext == ".html" and node.type in types_to_extract_html:
        name_node = None
        name = "html_element"
        chunks.append({
            "file_path": file_path,
            "chunk_type": types_to_extract_html[node.type],
            "name": name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "code_text": code_bytes[node.start_byte:node.end_byte].decode('utf8', errors='replace')
        })
    elif ext == ".css" and node.type in types_to_extract_css:
        name_node = None
        name = "css_rule"
        chunks.append({
            "file_path": file_path,
            "chunk_type": types_to_extract_css[node.type],
            "name": name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "code_text": code_bytes[node.start_byte:node.end_byte].decode('utf8', errors='replace')
        })

    for child in node.children:
        extract_nodes(child, code_bytes, ext, chunks, file_path)

def extract_chunks(file_path, code):
    ext = os.path.splitext(file_path)[1]
    parser = get_parser(ext)
    if not parser:
        return []

    code_bytes = code.encode("utf8")
    tree = parser.parse(code_bytes)
    
    chunks = []
    extract_nodes(tree.root_node, code_bytes, ext, chunks, file_path)
    return chunks

def ingest_repo(github_url):
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"Cloning {github_url} into {temp_dir}...")
        Repo.clone_from(github_url, temp_dir, depth=1)
        all_chunks = []
        for root, dirs, files in os.walk(temp_dir):
            if ".git" in dirs:
                dirs.remove(".git")
            if "node_modules" in dirs:
                dirs.remove("node_modules")
                
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in [".py", ".js", ".jsx", ".java", ".cpp", ".cc", ".cxx", ".hpp", ".h", ".dart", ".php", ".html", ".css"]:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, temp_dir)
                    
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                            if len(lines) > 2000:
                                continue
                            code = "".join(lines)
                            
                        chunks = extract_chunks(rel_path, code)
                        all_chunks.extend(chunks)
                    except Exception as e:
                        print(f"Error parsing {rel_path}: {e}")
                        pass
                        
        return all_chunks
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def get_repo_tree(github_url):
    temp_dir = tempfile.mkdtemp()
    try:
        Repo.clone_from(github_url, temp_dir, depth=1)
        
        def build_tree(dir_path):
            tree = []
            for item in os.listdir(dir_path):
                if item in ['.git', 'node_modules', 'vendor', '__pycache__', '.venv', 'venv']:
                    continue
                
                item_path = os.path.join(dir_path, item)
                if os.path.isdir(item_path):
                    tree.append({
                        "name": item,
                        "type": "folder",
                        "children": build_tree(item_path)
                    })
                else:
                    tree.append({
                        "name": item,
                        "type": "file"
                    })
            # Sort folders first, then files, both alphabetically
            tree.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
            return tree
            
        return build_tree(temp_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def extract_schema_files(github_url):
    temp_dir = tempfile.mkdtemp()
    try:
        Repo.clone_from(github_url, temp_dir, depth=1)
        schema_code = ""
        
        # Look for typical database schema files
        valid_extensions = ['.sql', '.prisma']
        valid_filenames = ['schema.rb', 'models.py', 'database.py', 'db.py']
        
        for root, dirs, files in os.walk(temp_dir):
            if ".git" in dirs: dirs.remove(".git")
            if "node_modules" in dirs: dirs.remove("node_modules")
            if "vendor" in dirs: dirs.remove("vendor")
            if "venv" in dirs: dirs.remove("venv")
                
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                is_schema = ext in valid_extensions or file.lower() in valid_filenames
                
                # Also include PHP files with "migration" or "schema" or "model" in name or path
                if ext == '.php' and any(keyword in file.lower() or keyword in root.lower() for keyword in ['migration', 'schema', 'model']):
                    is_schema = True
                    
                if is_schema:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, temp_dir)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            # basic heuristic: limit file size
                            if len(content) < 50000 and content.strip():
                                schema_code += f"\n--- {rel_path} ---\n{content}\n"
                    except Exception:
                        pass
        
        # If schema_code is too long, truncate it to avoid LLM context limits
        max_chars = 30000 
        if len(schema_code) > max_chars:
            schema_code = schema_code[:max_chars] + "\n... (truncated due to size limits)"
            
        return schema_code
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


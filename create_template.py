import os
import zipfile

BASE_DIR = "azure-enterprise-demo"

def create_structure():
    folders = [
        f"{BASE_DIR}/terraform-agents",
        f"{BASE_DIR}/terraform-database"
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)

def create_files():
    files = {
        f"{BASE_DIR}/terraform-agents/main.tf": "provider \"azurerm\" { features {} }",
        f"{BASE_DIR}/terraform-database/main.tf": "provider \"azurerm\" { features {} }",
        f"{BASE_DIR}/azure-pipelines.yml": "trigger:\n- main",
        f"{BASE_DIR}/README.md": "# Azure Enterprise Demo"
    }

    for path, content in files.items():
        with open(path, "w") as f:
            f.write(content)

def create_zip():
    zip_name = f"{BASE_DIR}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                zipf.write(full_path)
    print("ZIP created:", zip_name)

if __name__ == "__main__":
    print("Creating folder structure...")
    create_structure()

    print("Creating files...")
    create_files()

    print("Creating zip...")
    create_zip()

    print("Done.")
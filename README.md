#🚀 AutoSiteGen – AI-Powered Website Generator

AutoSiteGen is an AI-powered system that automatically generates fully functional, UI-styled web applications from a single natural language prompt.
The user only needs to run npm run dev to see the generated website running.

The system supports multiple applications (Calculator, Todo, FLAMES, Food Ordering apps, etc.) without overwriting previous outputs.

🎯 Key Features

One prompt → one complete web application

Generates fully functional React applications

Uses Tailwind CSS for modern UI

Automatic project bootstrapping

Automatic dependency installation (npm install)

Supports multiple generated apps (no overwrite)

Strict validation to avoid broken or placeholder apps

🧠 High-Level Architecture
User Prompt
   ↓
Planner Agent
   ↓
Architect Agent
   ↓
Coder Agent
   ↓
Validator Agent
   ↓
Project Bootstrap + Auto npm install
   ↓
Generated Website (React + Vite + Tailwind)

🧩 Agent Responsibilities
1️⃣ Planner Agent

Understands the user’s intent

Identifies application type (logic-heavy, data-driven, UI-heavy)

Expands short user prompts into structured requirements

2️⃣ Architect Agent

Designs component structure

Defines pages, components, and data flow

Decides state and behavior requirements

3️⃣ Coder Agent

Generates actual React code

Implements real logic (not placeholders)

Uses Tailwind CSS for UI

Uses default exports consistently

4️⃣ Validator Agent

Ensures the app is runnable

Checks:

Logic implementation

UI styling presence

Export/import consistency

JSX validity

Blocks broken or incomplete output

⚙️ Workflow (Step-by-Step)

User provides a simple prompt

Create a FLAMES calculator website with a good UI


System creates a new app folder

generated-sites/app-XXX-project-name


A preconfigured React + Vite + Tailwind template is copied

Agents generate application-specific code inside src/

Validator verifies correctness and UI rules

npm install runs automatically

App is ready to run using:

npm run dev

🏗️ Project Structure
autositeiten/
│
├── agents/
│   ├── planner.py
│   ├── architect.py
│   ├── coder.py
│   └── validator.py
│
├── templates/
│   └── react-vite-tailwind/
│
├── utils/
│   ├── llm_client.py
│   ├── file_writer.py
│   └── helpers.py
│
├── generated-sites/
│   ├── app-001-calculator/
│   ├── app-002-todo/
│   └── app-003-flames/
│
├── graph/
│   ├── flow.py
│   └── state.py
│
└── main.py

▶️ How to Run the Project
1️⃣ Clone the Repository
git clone https://github.com/<your-username>/autositeiten.git
cd autositeiten

2️⃣ Install Python Dependencies
pip install -r requirements.txt

3️⃣ Generate an Application
python main.py "Create a simple Todo app"

4️⃣ Run the Generated App
cd generated-sites/app-XXX-your-app-name
npm run dev


👉 No need to run npm install manually — it is handled automatically.

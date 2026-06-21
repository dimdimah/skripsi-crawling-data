import re


SKILLS_DB = [
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang",
    "rust", "kotlin", "swift", "php", "ruby", "scala", "r", "dart",
    "shell", "bash", "powershell",

    # Web Frontend
    "react", "react native", "vue", "vue.js", "angular", "next.js", "nextjs",
    "nuxt", "svelte", "html", "css", "scss", "sass", "less", "tailwind",
    "bootstrap", "jquery",

    # Web Backend
    "node.js", "nodejs", "express", "django", "flask", "fastapi", "spring",
    "spring boot", "laravel", "rails", "asp.net", ".net", "gin", "echo",

    # Database
    "postgresql", "postgres", "mysql", "mariadb", "sqlite", "mongodb",
    "mongo", "redis", "elasticsearch", "cassandra", "dynamodb", "sql server",
    "oracle", "firebase", "supabase",

    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
    "jenkins", "gitlab ci", "github actions", "circleci", "ansible", "nginx",
    "linux", "ci/cd",

    # Tools & Platforms
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "slack",
    "figma", "postman",

    # Data & ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
    "pandas", "numpy", "matplotlib", "data analysis", "data science",
    "natural language processing", "nlp", "computer vision",

    # Mobile
    "flutter", "react native", "ios", "android", "swift", "kotlin",

    # Testing
    "selenium", "jest", "pytest", "mocha", "cypress", "unit testing",
    "integration testing",

    # Methodologies & Soft Skills
    "agile", "scrum", "kanban", "rest api", "graphql", "microservices",
    "oauth", "jwt", "design patterns", "oop", "mvc",

    # UI/UX
    "ui design", "ux design", "ui/ux", "wireframe", "prototype",
]


def extract_skills(text):
    """Extract skills from job description text using keyword matching."""
    if not text:
        return []

    text_lower = text.lower()
    found = []

    for skill in SKILLS_DB:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)

    return list(set(found))

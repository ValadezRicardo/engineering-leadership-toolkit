#!/bin/bash

# Setup Development Environment Script
# Automated setup for new developers joining the team
# Author: Ricardo Valadez
# Last Updated: 2024-05-24

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPANY_NAME="YourCompany"
PROJECT_NAME="engineering-platform"
REQUIRED_NODE_VERSION="18"
REQUIRED_PYTHON_VERSION="3.9"
REQUIRED_GO_VERSION="1.21"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on supported OS
check_os() {
    log_info "Checking operating system..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        DISTRO=$(lsb_release -si 2>/dev/null || echo "Unknown")
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        DISTRO="Windows"
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    log_success "Detected OS: $DISTRO"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Homebrew (macOS) or equivalent package managers
install_package_manager() {
    log_info "Installing package manager..."
    
    case $OS in
        "macos")
            if ! command_exists brew; then
                log_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                log_success "Homebrew installed successfully"
            else
                log_success "Homebrew already installed"
            fi
            ;;
        "linux")
            if command_exists apt-get; then
                sudo apt-get update
                sudo apt-get install -y curl wget git build-essential
            elif command_exists yum; then
                sudo yum update -y
                sudo yum install -y curl wget git gcc gcc-c++ make
            else
                log_error "No supported package manager found"
                exit 1
            fi
            log_success "Package manager updated"
            ;;
        "windows")
            if ! command_exists choco; then
                log_info "Installing Chocolatey..."
                powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
                log_success "Chocolatey installed successfully"
            else
                log_success "Chocolatey already installed"
            fi
            ;;
    esac
}

# Install Git and configure
setup_git() {
    log_info "Setting up Git..."
    
    if ! command_exists git; then
        case $OS in
            "macos")
                brew install git
                ;;
            "linux")
                if command_exists apt-get; then
                    sudo apt-get install -y git
                elif command_exists yum; then
                    sudo yum install -y git
                fi
                ;;
            "windows")
                choco install git -y
                ;;
        esac
        log_success "Git installed successfully"
    else
        log_success "Git already installed"
    fi
    
    # Configure Git if not already configured
    if [[ -z $(git config --global user.name) ]]; then
        read -p "Enter your full name for Git: " git_name
        git config --global user.name "$git_name"
    fi
    
    if [[ -z $(git config --global user.email) ]]; then
        read -p "Enter your email for Git: " git_email
        git config --global user.email "$git_email"
    fi
    
    # Set up useful Git aliases
    git config --global alias.co checkout
    git config --global alias.br branch
    git config --global alias.ci commit
    git config --global alias.st status
    git config --global alias.unstage 'reset HEAD --'
    git config --global alias.last 'log -1 HEAD'
    git config --global alias.visual '!gitk'
    
    # Set default branch name
    git config --global init.defaultBranch main
    
    # Set up better logging
    git config --global log.oneline true
    git config --global pull.rebase true
    
    log_success "Git configured successfully"
}

# Install Node.js and npm
install_nodejs() {
    log_info "Installing Node.js..."
    
    # Install Node Version Manager (nvm)
    if ! command_exists nvm; then
        case $OS in
            "macos"|"linux")
                curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
                export NVM_DIR="$HOME/.nvm"
                [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
                ;;
            "windows")
                choco install nvm -y
                ;;
        esac
        log_success "NVM installed successfully"
    fi
    
    # Install and use required Node.js version
    if command_exists nvm; then
        nvm install $REQUIRED_NODE_VERSION
        nvm use $REQUIRED_NODE_VERSION
        nvm alias default $REQUIRED_NODE_VERSION
    else
        # Fallback: install Node.js directly
        case $OS in
            "macos")
                brew install node@$REQUIRED_NODE_VERSION
                ;;
            "linux")
                curl -fsSL https://deb.nodesource.com/setup_${REQUIRED_NODE_VERSION}.x | sudo -E bash -
                sudo apt-get install -y nodejs
                ;;
            "windows")
                choco install nodejs --version=$REQUIRED_NODE_VERSION -y
                ;;
        esac
    fi
    
    # Verify installation
    if command_exists node && command_exists npm; then
        NODE_VERSION=$(node --version)
        NPM_VERSION=$(npm --version)
        log_success "Node.js $NODE_VERSION and npm $NPM_VERSION installed successfully"
    else
        log_error "Failed to install Node.js"
        exit 1
    fi
    
    # Install global npm packages
    log_info "Installing global npm packages..."
    npm install -g @angular/cli typescript eslint prettier nodemon pm2
    log_success "Global npm packages installed"
}

# Install Python and pip
install_python() {
    log_info "Installing Python..."
    
    case $OS in
        "macos")
            brew install python@$REQUIRED_PYTHON_VERSION
            ;;
        "linux")
            sudo apt-get install -y python$REQUIRED_PYTHON_VERSION python$REQUIRED_PYTHON_VERSION-pip python$REQUIRED_PYTHON_VERSION-venv
            ;;
        "windows")
            choco install python --version=$REQUIRED_PYTHON_VERSION -y
            ;;
    esac
    
    # Verify installation
    if command_exists python3 && command_exists pip3; then
        PYTHON_VERSION=$(python3 --version)
        PIP_VERSION=$(pip3 --version)
        log_success "$PYTHON_VERSION and pip installed successfully"
    else
        log_error "Failed to install Python"
        exit 1
    fi
    
    # Install common Python packages
    log_info "Installing common Python packages..."
    pip3 install --user virtualenv pytest black flake8 mypy requests pandas numpy
    log_success "Python packages installed"
}

# Install Go
install_go() {
    log_info "Installing Go..."
    
    case $OS in
        "macos")
            brew install go
            ;;
        "linux")
            # Download and install Go
            GO_VERSION="1.21.0"
            wget -c https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz
            sudo rm -rf /usr/local/go
            sudo tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz
            rm go${GO_VERSION}.linux-amd64.tar.gz
            
            # Add to PATH
            echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
            echo 'export GOPATH=$HOME/go' >> ~/.bashrc
            echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc
            source ~/.bashrc
            ;;
        "windows")
            choco install golang -y
            ;;
    esac
    
    # Verify installation
    if command_exists go; then
        GO_VERSION=$(go version)
        log_success "$GO_VERSION installed successfully"
    else
        log_error "Failed to install Go"
        exit 1
    fi
}

# Install Docker
install_docker() {
    log_info "Installing Docker..."
    
    case $OS in
        "macos")
            if ! command_exists docker; then
                log_info "Please install Docker Desktop for Mac from https://docs.docker.com/desktop/mac/install/"
                log_warning "Manual installation required for Docker on macOS"
            else
                log_success "Docker already installed"
            fi
            ;;
        "linux")
            # Install Docker
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            rm get-docker.sh
            
            # Add user to docker group
            sudo usermod -aG docker $USER
            
            # Install Docker Compose
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            ;;
        "windows")
            log_info "Please install Docker Desktop for Windows from https://docs.docker.com/desktop/windows/install/"
            log_warning "Manual installation required for Docker on Windows"
            ;;
    esac
    
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version)
        log_success "$DOCKER_VERSION installed successfully"
    fi
}

# Install development tools
install_dev_tools() {
    log_info "Installing development tools..."
    
    case $OS in
        "macos")
            # Install essential tools via Homebrew
            brew install \
                wget \
                curl \
                jq \
                htop \
                tree \
                vim \
                tmux \
                postgresql \
                redis \
                awscli \
                kubectl \
                terraform \
                helm
            ;;
        "linux")
            # Install essential tools via apt/yum
            if command_exists apt-get; then
                sudo apt-get install -y \
                    wget \
                    curl \
                    jq \
                    htop \
                    tree \
                    vim \
                    tmux \
                    postgresql-client \
                    redis-tools
                
                # Install kubectl
                curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
                rm kubectl
                
                # Install Terraform
                wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
                echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
                sudo apt update && sudo apt install terraform
                
                # Install AWS CLI
                curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                unzip awscliv2.zip
                sudo ./aws/install
                rm -rf awscliv2.zip aws/
            fi
            ;;
        "windows")
            choco install \
                wget \
                curl \
                jq \
                vim \
                postgresql \
                redis \
                awscli \
                kubernetes-cli \
                terraform \
                kubernetes-helm -y
            ;;
    esac
    
    log_success "Development tools installed successfully"
}

# Setup IDE and extensions
setup_ide() {
    log_info "Setting up IDE configurations..."
    
    # Create VS Code settings directory
    case $OS in
        "macos")
            VSCODE_DIR="$HOME/Library/Application Support/Code/User"
            ;;
        "linux")
            VSCODE_DIR="$HOME/.config/Code/User"
            ;;
        "windows")
            VSCODE_DIR="$HOME/AppData/Roaming/Code/User"
            ;;
    esac
    
    mkdir -p "$VSCODE_DIR"
    
    # Create VS Code settings.json
    cat > "$VSCODE_DIR/settings.json" << 'EOF'
{
    "editor.tabSize": 2,
    "editor.insertSpaces": true,
    "editor.detectIndentation": false,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll.eslint": true
    },
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    "typescript.preferences.importModuleSpecifier": "relative",
    "python.defaultInterpreterPath": "/usr/bin/python3",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "go.formatTool": "goimports",
    "go.useLanguageServer": true,
    "git.autofetch": true,
    "git.confirmSync": false,
    "terminal.integrated.defaultProfile.linux": "bash",
    "terminal.integrated.defaultProfile.osx": "zsh",
    "workbench.colorTheme": "Dark+ (default dark)",
    "workbench.iconTheme": "vs-seti"
}
EOF
    
    # Install VS Code extensions via command line (if code command is available)
    if command_exists code; then
        log_info "Installing VS Code extensions..."
        
        # Essential extensions
        code --install-extension ms-vscode.vscode-typescript-next
        code --install-extension ms-python.python
        code --install-extension golang.go
        code --install-extension bradlc.vscode-tailwindcss
        code --install-extension esbenp.prettier-vscode
        code --install-extension dbaeumer.vscode-eslint
        code --install-extension ms-vscode.vscode-json
        code --install-extension redhat.vscode-yaml
        code --install-extension ms-kubernetes-tools.vscode-kubernetes-tools
        code --install-extension hashicorp.terraform
        code --install-extension ms-vscode.docker
        code --install-extension GitLab.gitlab-workflow
        code --install-extension github.copilot
        code --install-extension ms-vscode.live-server
        code --install-extension formulahendry.auto-rename-tag
        code --install-extension christian-kohler.path-intellisense
        
        log_success "VS Code extensions installed"
    else
        log_warning "VS Code command not found. Please install extensions manually."
    fi
}

# Setup shell configuration
setup_shell() {
    log_info "Setting up shell configuration..."
    
    # Determine shell
    CURRENT_SHELL=$(basename "$SHELL")
    
    case $CURRENT_SHELL in
        "bash")
            SHELL_RC="$HOME/.bashrc"
            ;;
        "zsh")
            SHELL_RC="$HOME/.zshrc"
            ;;
        *)
            log_warning "Unsupported shell: $CURRENT_SHELL"
            return
            ;;
    esac
    
    # Create shell configuration backup
    if [[ -f "$SHELL_RC" ]]; then
        cp "$SHELL_RC" "${SHELL_RC}.backup.$(date +%Y%m%d)"
    fi
    
    # Add development environment configurations
    cat >> "$SHELL_RC" << 'EOF'

# Development Environment Setup
export EDITOR=vim
export VISUAL=vim

# Node.js
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# Python
export PATH="$HOME/.local/bin:$PATH"

# Go
export GOPATH="$HOME/go"
export PATH="$PATH:/usr/local/go/bin:$GOPATH/bin"

# Useful aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Git aliases
alias gst='git status'
alias gco='git checkout'
alias gcb='git checkout -b'
alias gaa='git add .'
alias gcm='git commit -m'
alias gps='git push'
alias gpl='git pull'
alias glog='git log --oneline --graph --decorate'

# Docker aliases
alias dps='docker ps'
alias dpa='docker ps -a'
alias di='docker images'
alias dex='docker exec -it'
alias dlog='docker logs'
alias dcp='docker-compose'
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'

# Kubernetes aliases
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get services'
alias kgd='kubectl get deployments'
alias kdesc='kubectl describe'
alias klogs='kubectl logs'

# Project shortcuts
alias cdp='cd ~/projects'
alias cdw='cd ~/workspace'

# Development utilities
alias serve='python3 -m http.server 8000'
alias jsonpp='python3 -m json.tool'
alias urlencode='python3 -c "import sys, urllib.parse as ul; print(ul.quote_plus(sys.argv[1]))"'
alias urldecode='python3 -c "import sys, urllib.parse as ul; print(ul.unquote_plus(sys.argv[1]))"'

EOF
    
    # Source the updated configuration
    source "$SHELL_RC"
    
    log_success "Shell configuration updated"
}

# Create project directory structure
setup_project_structure() {
    log_info "Setting up project directory structure..."
    
    # Create standard directories
    mkdir -p ~/projects
    mkdir -p ~/workspace
    mkdir -p ~/scripts
    mkdir -p ~/docs
    
    # Create common configuration directories
    mkdir -p ~/.aws
    mkdir -p ~/.kube
    mkdir -p ~/.docker
    
    log_success "Project directory structure created"
}

# Generate SSH key for Git
setup_ssh_keys() {
    log_info "Setting up SSH keys..."
    
    if [[ ! -f ~/.ssh/id_rsa ]]; then
        read -p "Enter your email for SSH key: " ssh_email
        ssh-keygen -t rsa -b 4096 -C "$ssh_email" -f ~/.ssh/id_rsa -N ""
        
        # Start ssh-agent and add key
        eval "$(ssh-agent -s)"
        ssh-add ~/.ssh/id_rsa
        
        log_success "SSH key generated successfully"
        log_info "Public key saved to ~/.ssh/id_rsa.pub"
        log_warning "Please add this public key to your Git hosting service (GitHub, GitLab, etc.)"
        
        # Display public key
        echo "Your public SSH key:"
        echo "----------------------------------------"
        cat ~/.ssh/id_rsa.pub
        echo "----------------------------------------"
    else
        log_success "SSH key already exists"
    fi
}

# Setup environment variables template
setup_environment_variables() {
    log_info "Setting up environment variables template..."
    
    # Create .env template
    cat > ~/.env.template << 'EOF'
# Development Environment Variables Template
# Copy this file to .env in your project directories and fill in the values

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379

# API Keys (Get these from respective services)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-west-2

# Application Configuration
NODE_ENV=development
DEBUG=true
LOG_LEVEL=debug
PORT=3000

# Third-party Services
STRIPE_SECRET_KEY=sk_test_...
SENDGRID_API_KEY=SG....
SENTRY_DSN=https://...

# GitHub/GitLab Tokens (for CI/CD)
GITHUB_TOKEN=ghp_...
GITLAB_TOKEN=glpat-...

# Kubernetes/Docker Registry
DOCKER_REGISTRY=your-registry.com
KUBE_CONFIG_PATH=~/.kube/config

# Company-specific configurations
COMPANY_API_BASE_URL=https://api.company.com
INTERNAL_SERVICE_TOKEN=...

EOF
    
    log_success "Environment variables template created at ~/.env.template"
    log_info "Copy this template to your project directories and fill in actual values"
}

# Setup pre-commit hooks template
setup_precommit_hooks() {
    log_info "Setting up pre-commit hooks template..."
    
    mkdir -p ~/templates/git-hooks
    
    # Create pre-commit hook template
    cat > ~/templates/git-hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for code quality checks

set -e

echo "Running pre-commit checks..."

# Check for debugging statements
if grep -r "console.log\|debugger\|pdb.set_trace\|fmt.Print" --include="*.js" --include="*.ts" --include="*.py" --include="*.go" .; then
    echo "❌ Found debugging statements. Please remove them before committing."
    exit 1
fi

# Check for TODO/FIXME without issue numbers
if grep -r "TODO\|FIXME" --include="*.js" --include="*.ts" --include="*.py" --include="*.go" . | grep -v "#[0-9]"; then
    echo "⚠️  Found TODO/FIXME without issue numbers. Please add issue references."
fi

# Run linters if available
if command -v eslint >/dev/null 2>&1; then
    echo "Running ESLint..."
    eslint . --ext .js,.ts --fix
fi

if command -v black >/dev/null 2>&1; then
    echo "Running Black formatter..."
    black . --check
fi

if command -v gofmt >/dev/null 2>&1; then
    echo "Running Go formatter..."
    gofmt -l .
fi

# Run tests if available
if [[ -f "package.json" ]] && command -v npm >/dev/null 2>&1; then
    if grep -q '"test"' package.json; then
        echo "Running npm tests..."
        npm test
    fi
fi

if [[ -f "requirements.txt" ]] && command -v pytest >/dev/null 2>&1; then
    echo "Running Python tests..."
    pytest
fi

if [[ -f "go.mod" ]] && command -v go >/dev/null 2>&1; then
    echo "Running Go tests..."
    go test ./...
fi

echo "✅ All pre-commit checks passed!"
EOF
    
    chmod +x ~/templates/git-hooks/pre-commit
    
    log_success "Pre-commit hook template created at ~/templates/git-hooks/pre-commit"
    log_info "Copy this to .git/hooks/pre-commit in your project repositories"
}

# Setup development databases (optional)
setup_development_databases() {
    log_info "Setting up development databases..."
    
    if command_exists docker; then
        log_info "Starting PostgreSQL and Redis containers..."
        
        # PostgreSQL
        docker run -d \
            --name dev-postgres \
            -e POSTGRES_PASSWORD=dev_password \
            -e POSTGRES_USER=dev_user \
            -e POSTGRES_DB=dev_database \
            -p 5432:5432 \
            postgres:13-alpine
        
        # Redis
        docker run -d \
            --name dev-redis \
            -p 6379:6379 \
            redis:6-alpine
        
        log_success "Development databases started"
        log_info "PostgreSQL: localhost:5432 (user: dev_user, password: dev_password)"
        log_info "Redis: localhost:6379"
    else
        log_warning "Docker not available. Skipping database setup."
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    echo ""
    echo "=== Installation Verification ==="
    
    # Check each tool
    tools=(
        "git:Git"
        "node:Node.js"
        "npm:npm"
        "python3:Python"
        "pip3:pip"
        "go:Go"
        "docker:Docker"
        "kubectl:Kubernetes CLI"
        "terraform:Terraform"
        "aws:AWS CLI"
    )
    
    for tool_info in "${tools[@]}"; do
        IFS=':' read -r cmd name <<< "$tool_info"
        if command_exists "$cmd"; then
            version=$($cmd --version 2>/dev/null | head -n1 || echo "installed")
            echo "✅ $name: $version"
        else
            echo "❌ $name: not found"
        fi
    done
    
    echo ""
    echo "=== Directory Structure ==="
    echo "📁 ~/projects (for personal projects)"
    echo "📁 ~/workspace (for work projects)"
    echo "📁 ~/scripts (for utility scripts)"
    echo "📁 ~/docs (for documentation)"
    echo ""
    
    echo "=== Next Steps ==="
    echo "1. Restart your terminal to ensure all changes take effect"
    echo "2. Clone your first repository: git clone <repository-url>"
    echo "3. Copy ~/.env.template to your project and fill in values"
    echo "4. Set up pre-commit hooks in your repositories"
    echo "5. Add your SSH public key to Git hosting services"
    echo ""
    
    log_success "Development environment setup complete!"
}

# Main execution flow
main() {
    echo "🚀 Development Environment Setup Script"
    echo "======================================"
    echo ""
    
    # Check if script is run with sudo (we don't want that for most operations)
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root/sudo"
        log_info "Run as regular user: ./setup-dev-environment.sh"
        exit 1
    fi
    
    # Confirm before proceeding
    read -p "This will install development tools and configure your environment. Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Setup cancelled by user"
        exit 0
    fi
    
    echo ""
    log_info "Starting development environment setup..."
    echo ""
    
    # Run setup steps
    check_os
    install_package_manager
    setup_git
    install_nodejs
    install_python
    install_go
    install_docker
    install_dev_tools
    setup_ide
    setup_shell
    setup_project_structure
    setup_ssh_keys
    setup_environment_variables
    setup_precommit_hooks
    
    # Optional: setup development databases
    read -p "Set up development databases with Docker? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_development_databases
    fi
    
    verify_installation
}

# Run main function
main "$@"
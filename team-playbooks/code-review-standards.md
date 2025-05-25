# Code Review Standards

**Comprehensive guide for effective code reviews that maintain high quality and foster team growth**

## 🎯 Code Review Objectives

### Code Quality
- **Detect bugs** before they reach production
- **Maintain consistency** in style and patterns
- **Ensure performance** and scalability
- **Validate security** and error handling

### Team Development
- **Share knowledge** between developers
- **Mentor** junior developers
- **Spread best practices** and patterns
- **Foster collaboration** and communication

### Maintainability
- **Readable code** and proper documentation
- **Coherent architecture** with team decisions
- **Adequate testing** and sufficient coverage
- **Updated documentation** when necessary

## 📋 Code Review Process

### 1. Before Creating a Pull Request

**Developer submitting code:**
- [ ] **Self-review:** Review your own code before submitting
- [ ] **Tests passing:** All tests pass locally
- [ ] **Clean linting:** No style or lint errors
- [ ] **Atomic commits:** Each commit represents a logical change
- [ ] **Clear description:** PR description explains what, why, and how

**Pre-Submit Checklist:**
- [ ] Code compiles without warnings
- [ ] New unit tests for new functionality
- [ ] Regression tests updated if necessary
- [ ] Documentation updated (README, API docs, etc.)
- [ ] No hardcoded credentials or sensitive information
- [ ] Performance considered for critical changes

### 2. Pull Request Structure

#### Descriptive Title
```
[TYPE]: Concise description of change

Examples:
feat: Add user authentication middleware
fix: Resolve memory leak in payment processing
refactor: Simplify order validation logic
docs: Update API documentation for v2 endpoints
```

#### Detailed Description
```markdown
## What changes?
Clear description of functionality or fix implemented

## Why?
Context of the problem or need this PR solves

## How?
Technical approach used and important decisions

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests verified
- [ ] Manual testing completed

## Checklist
- [ ] Code self-reviewed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Performance verified
```

### 3. Reviewer Assignment

#### Selection Criteria
- **Expertise:** At least one reviewer with area knowledge
- **Availability:** Reviewers who can respond within <24 hours
- **Diversity:** Include different experience levels when possible
- **Ownership:** Automatic code owners for critical areas

#### Number of Reviewers
- **Small changes** (< 50 lines): 1 reviewer
- **Medium changes** (50-200 lines): 2 reviewers
- **Large changes** (> 200 lines): 2-3 reviewers + architect
- **Critical changes** (security, payments): 3+ reviewers + security review

### 4. Expected Timeline

| PR Size | Review Time | Response SLA |
|---------|-------------|--------------|
| XS (< 20 lines) | 30 minutes | 4 hours |
| S (20-50 lines) | 1 hour | 8 hours |
| M (50-200 lines) | 2-4 hours | 24 hours |
| L (200-500 lines) | 4-8 hours | 48 hours |
| XL (> 500 lines) | Split into smaller PRs | N/A |

## 🔍 What to Review

### 1. Functionality and Logic

#### Correctness
- [ ] **Code does what it claims to do**
- [ ] **Edge cases are handled** appropriately
- [ ] **Input validation** is robust
- [ ] **Error handling** is complete and appropriate

#### Performance
- [ ] **Efficient DB queries** (no N+1, proper indexes)
- [ ] **Optimized algorithms** for the use case
- [ ] **Memory leaks** prevented
- [ ] **Caching implemented** where beneficial

### 2. Code and Style

#### Readability
- [ ] **Descriptive names** for variables, functions, and classes
- [ ] **Small functions** with single responsibility
- [ ] **Useful comments** that explain "why", not "what"
- [ ] **Self-documenting code** when possible

#### Consistency
- [ ] **Consistent style** with rest of codebase
- [ ] **Established patterns** followed correctly
- [ ] **Naming conventions** respected
- [ ] **Directory structure** appropriate

### 3. Architecture and Design

#### SOLID Principles
- [ ] **Single Responsibility:** Each class/function has one responsibility
- [ ] **Open/Closed:** Open for extension, closed for modification
- [ ] **Liskov Substitution:** Subtypes substitutable for their base types
- [ ] **Interface Segregation:** Specific interfaces better than general ones
- [ ] **Dependency Inversion:** Depend on abstractions, not concretions

#### Patterns and Practices
- [ ] **DRY (Don't Repeat Yourself):** Logic not duplicated
- [ ] **YAGNI (You Ain't Gonna Need It):** No over-engineering
- [ ] **Separation of Concerns:** Responsibilities well separated
- [ ] **Dependency Injection:** Dependencies injected, not hardcoded

### 4. Testing and Quality

#### Test Coverage
- [ ] **Unit tests** for new functionality
- [ ] **Integration tests** for critical flows
- [ ] **Edge case tests** implemented
- [ ] **Appropriate mocks** for external dependencies

#### Test Quality
- [ ] **Clear and readable tests** with descriptive naming
- [ ] **Arrange-Act-Assert** pattern followed
- [ ] **Independent tests** that don't depend on order
- [ ] **Realistic test data** but not real data

### 5. Security

#### Common Vulnerabilities
- [ ] **SQL Injection** prevented with prepared statements
- [ ] **XSS** prevented with proper escaping
- [ ] **CSRF** protected with appropriate tokens
- [ ] **Authentication/Authorization** implemented correctly

#### Sensitive Data
- [ ] **No hardcoded credentials** in code
- [ ] **Logs don't contain** sensitive information
- [ ] **Personal data** handled according to GDPR/regulations
- [ ] **Appropriate encryption** for sensitive data

## 💬 How to Give Effective Feedback

### 1. Comment Types

#### Use Clear Prefixes
- **`nit:`** Minor comment, non-blocking
- **`question:`** Question to understand better
- **`suggestion:`** Optional improvement proposal
- **`issue:`** Problem that must be fixed
- **`critical:`** Serious problem that blocks merge

#### Examples of Constructive Comments

**❌ Poor feedback:**
```
"This code is wrong"
"I don't like this approach"
"This won't work"
```

**✅ Good feedback:**
```
"suggestion: Consider using Array.reduce() here for better readability:
[suggested code]

"issue: This function can throw an exception if `user` is null. 
Suggest adding validation:
if (!user) { throw new Error('User is required'); }

"question: Why did you choose Promise.all() here instead of Promise.allSettled()? 
With the current approach, if one request fails, all fail."
```

### 2. Feedback Principles

#### Focus on Code, Not Person
- **Good:** "This function is complex"
- **Bad:** "You don't understand how to write simple code"

#### Be Specific and Constructive
- **Explain the problem** clearly
- **Suggest alternatives** when possible
- **Include code examples** when useful
- **Link relevant documentation**

#### Celebrate Good Code
- **Recognize good design decisions**
- **Highlight elegant code** or creative solutions
- **Learn publicly** when you see something new

### 3. Handling Disagreements

#### Escalation Process
1. **Direct discussion** in PR comments
2. **Quick call** to clarify complex points
3. **Involve tech lead** for architectural decisions
4. **Team meeting** for patterns affecting entire team

#### Conflict Resolution Principles
- **Data over opinions:** Use metrics and benchmarks
- **Consistency over preference:** Follow team standards
- **Pragmatism over perfection:** Balance ideal vs. reality
- **Learning mindset:** See disagreements as growth opportunities

## 🚀 Best Practices for Reviewers

### 1. Review Preparation

#### Necessary Context
- [ ] **Read complete description** of the PR
- [ ] **Understand the problem** being solved
- [ ] **Review related tickets** (Jira, Linear, etc.)
- [ ] **Verify CI** is passing

#### Environment Setup
- [ ] **Pull the branch** for local testing if necessary
- [ ] **Run tests** locally for complex changes
- [ ] **Verify app** works correctly

### 2. Review Strategy

#### Review Order
1. **Description and context** - Does the PR solve the right problem?
2. **General architecture** - Is the approach sound?
3. **Tests** - Are they complete and well-written?
4. **Implementation** - Is the code correct and clean?
5. **Details and style** - Does it follow conventions?

#### Effective Techniques
- **Start with big picture** before going to details
- **Read as a user** of the code, not just as reviewer
- **Think about maintenance** - Will it be easy to modify in the future?
- **Consider performance** especially for critical code

### 3. Communication During Review

#### Response Timing
- **Acknowledge receipt** within 4 hours
- **Complete review** within defined SLA
- **Quick clarifications** respond ASAP
- **Follow up** if no response in 24 hours

#### Tool Usage
- **GitHub suggestions** for specific code changes
- **Inline comments** for contextual feedback
- **General comments** for architectural feedback
- **Direct messages** for complex discussions

## 📊 Metrics and Continuous Improvement

### 1. Code Review KPIs

#### Process Efficiency
- **Review time:** Average review time by PR size
- **Pickup time:** Time until someone takes the review
- **Iteration cycles:** Average round-trips per PR
- **Merge time:** Total time from PR creation to merge

#### Output Quality
- **Bug detection rate:** Bugs found in review vs. production
- **Rework percentage:** PRs requiring significant changes
- **Test coverage impact:** Coverage change per merged PR
- **Technical debt reduction:** Architectural improvements per quarter

### 2. Feedback and Retrospectives

#### Process Review (Monthly)
- **What's working well?** in our current process
- **What can we improve?** to be more effective
- **Are there bottlenecks?** slowing down development
- **Do we need training?** in any specific area

#### Team Health Surveys
- **Satisfaction with review process** (1-5 scale)
- **Learning from reviews** - Are you learning?
- **Feedback quality** - Is it constructive and useful?
- **Time allocation** - Is the time invested sustainable?

### 3. Improvement Actions

#### Automation Opportunities
- **Linting and formatting** automated pre-commit
- **Security scanning** integrated in CI
- **Performance regression** automatic detection
- **Test coverage** requirements enforcement

#### Process Refinement
- **Review checklist** updates based on recurring bugs
- **Training sessions** for specific patterns
- **Tool improvements** for better developer experience
- **Documentation updates** to clarify standards

## 🛠️ Tools and Configuration

### 1. GitHub Configuration

#### Branch Protection Rules
```yaml
require_status_checks: true
required_status_checks:
  - CI/Tests
  - Security Scan
  - Code Coverage
require_pull_request_reviews: true
required_approving_review_count: 2
dismiss_stale_reviews: true
require_code_owner_reviews: true
```

#### PR Template
```markdown
## Description
[Describe what this PR does]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### 2. Automated Checks

#### Pre-commit Hooks
```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: eslint
        name: ESLint
        entry: npm run lint
        language: system
        types: [javascript]
      
      - id: tests
        name: Tests
        entry: npm test
        language: system
        pass_filenames: false
      
      - id: security-check
        name: Security Check
        entry: npm audit
        language: system
        pass_filenames: false
```

#### CI Pipeline Integration
```yaml
# .github/workflows/pr-checks.yml
name: PR Checks
on: pull_request

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linting
        run: npm run lint
      
      - name: Run tests
        run: npm test
      
      - name: Check coverage
        run: npm run coverage
      
      - name: Security audit
        run: npm audit
      
      - name: Build check
        run: npm run build
```

### 3. Code Quality Tools

#### ESLint Configuration
```json
{
  "extends": [
    "@typescript-eslint/recommended",
    "prettier"
  ],
  "rules": {
    "no-console": "warn",
    "no-debugger": "error",
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "complexity": ["error", 10],
    "max-lines-per-function": ["error", 50],
    "max-depth": ["error", 4]
  }
}
```

#### Prettier Configuration
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

#### SonarQube Quality Gates
```xml
<!-- sonar-project.properties -->
sonar.projectKey=your-project
sonar.sources=src
sonar.tests=tests
sonar.coverage.exclusions=**/*.test.js,**/*.spec.js
sonar.javascript.lcov.reportPaths=coverage/lcov.info

<!-- Quality Gate Conditions -->
sonar.qualitygate.wait=true
sonar.coverage.minimum=80
sonar.duplicated_lines_density.maximum=3
sonar.maintainability_rating.minimum=A
sonar.reliability_rating.minimum=A
sonar.security_rating.minimum=A
```

## 📚 Language-Specific Guidelines

### JavaScript/TypeScript
```typescript
// ✅ Good: Clear, typed, and documented
interface UserService {
  createUser(userData: CreateUserRequest): Promise<User>;
  getUserById(id: string): Promise<User | null>;
}

class UserServiceImpl implements UserService {
  constructor(private readonly userRepository: UserRepository) {}

  async createUser(userData: CreateUserRequest): Promise<User> {
    // Validate input
    if (!userData.email || !userData.name) {
      throw new ValidationError('Email and name are required');
    }

    // Check for existing user
    const existingUser = await this.userRepository.findByEmail(userData.email);
    if (existingUser) {
      throw new ConflictError('User already exists');
    }

    return this.userRepository.create(userData);
  }
}

// ❌ Bad: Unclear, untyped, no error handling
function createUser(data: any) {
  return userRepo.create(data);
}
```

### Python
```python
# ✅ Good: Clear, typed, and follows PEP 8
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class User:
    id: str
    email: str
    name: str

class UserService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def create_user(self, user_data: dict) -> User:
        """Create a new user with validation."""
        if not user_data.get('email') or not user_data.get('name'):
            raise ValueError('Email and name are required')

        existing_user = self._user_repository.find_by_email(user_data['email'])
        if existing_user:
            raise ConflictError('User already exists')

        return self._user_repository.create(user_data)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve user by ID, return None if not found."""
        return self._user_repository.find_by_id(user_id)

# ❌ Bad: No types, unclear names, no validation
def create_user(data):
    return repo.create(data)
```

### Go
```go
// ✅ Good: Clear, idiomatic Go with proper error handling
package user

import (
    "errors"
    "fmt"
)

type User struct {
    ID    string `json:"id"`
    Email string `json:"email"`
    Name  string `json:"name"`
}

type Service struct {
    repo Repository
}

func NewService(repo Repository) *Service {
    return &Service{repo: repo}
}

func (s *Service) CreateUser(email, name string) (*User, error) {
    if email == "" || name == "" {
        return nil, errors.New("email and name are required")
    }

    existingUser, err := s.repo.FindByEmail(email)
    if err != nil {
        return nil, fmt.Errorf("failed to check existing user: %w", err)
    }
    if existingUser != nil {
        return nil, errors.New("user already exists")
    }

    user := &User{
        Email: email,
        Name:  name,
    }

    if err := s.repo.Create(user); err != nil {
        return nil, fmt.Errorf("failed to create user: %w", err)
    }

    return user, nil
}

// ❌ Bad: No error handling, unclear interface
func CreateUser(email, name string) *User {
    return repo.Create(email, name)
}
```

## 🏆 Code Review Champions Program

### Recognition Levels
- **Code Review Rookie:** Completed first 10 meaningful reviews
- **Review Contributor:** Consistent quality reviews for 3 months
- **Review Mentor:** Helps others improve review skills
- **Review Champion:** Drives process improvements and training

### Monthly Recognition
- **Most Helpful Reviewer:** Based on developer feedback
- **Best Learning Comment:** Comment that taught others something new
- **Process Improver:** Suggestion that improved team efficiency

---

**Remember:** Code review is a collaboration tool, not a judgment. The goal is to improve code quality, share knowledge, and grow together as a team. Focus on the code, be constructive, and celebrate learning opportunities
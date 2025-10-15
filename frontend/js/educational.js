/**
 * Educational Content JavaScript
 * Handles educational content, trading journal, learning paths, goals, and quizzes
 */

class EducationalManager {
    constructor() {
        this.apiBase = 'http://localhost:8000/api/v1/educational';
        this.currentTab = 'content';
        this.init();
    }

    async init() {
        await this.loadContentTypes();
        await this.loadDifficultyLevels();
        await this.loadJournalEntryTypes();
        this.setupEventListeners();
        this.loadContent();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const target = e.target.getAttribute('data-bs-target');
                this.currentTab = target.replace('#', '');
                this.loadTabContent();
            });
        });

        // Filter changes
        document.getElementById('contentTypeFilter')?.addEventListener('change', () => this.applyFilters());
        document.getElementById('difficultyFilter')?.addEventListener('change', () => this.applyFilters());
    }

    async loadContentTypes() {
        try {
            const response = await fetch(`${this.apiBase}/content-types`);
            const data = await response.json();
            
            const contentTypeSelect = document.getElementById('contentType');
            const contentTypeFilter = document.getElementById('contentTypeFilter');
            
            if (contentTypeSelect) {
                contentTypeSelect.innerHTML = '<option value="">Select Type</option>';
                data.content_types.forEach(type => {
                    contentTypeSelect.innerHTML += `<option value="${type.type}">${type.name}</option>`;
                });
            }
            
            if (contentTypeFilter) {
                contentTypeFilter.innerHTML = '<option value="">All Types</option>';
                data.content_types.forEach(type => {
                    contentTypeFilter.innerHTML += `<option value="${type.type}">${type.name}</option>`;
                });
            }
        } catch (error) {
            console.error('Error loading content types:', error);
        }
    }

    async loadDifficultyLevels() {
        try {
            const response = await fetch(`${this.apiBase}/difficulty-levels`);
            const data = await response.json();
            
            const difficultySelects = [
                'contentDifficulty', 'pathDifficulty', 'quizDifficulty'
            ];
            const difficultyFilter = document.getElementById('difficultyFilter');
            
            difficultySelects.forEach(selectId => {
                const select = document.getElementById(selectId);
                if (select) {
                    select.innerHTML = '<option value="">Select Level</option>';
                    data.difficulty_levels.forEach(level => {
                        select.innerHTML += `<option value="${level.level}">${level.name}</option>`;
                    });
                }
            });
            
            if (difficultyFilter) {
                difficultyFilter.innerHTML = '<option value="">All Levels</option>';
                data.difficulty_levels.forEach(level => {
                    difficultyFilter.innerHTML += `<option value="${level.level}">${level.name}</option>`;
                });
            }
        } catch (error) {
            console.error('Error loading difficulty levels:', error);
        }
    }

    async loadJournalEntryTypes() {
        try {
            const response = await fetch(`${this.apiBase}/journal-entry-types`);
            const data = await response.json();
            
            const journalTypeSelect = document.getElementById('journalType');
            if (journalTypeSelect) {
                journalTypeSelect.innerHTML = '<option value="">Select Type</option>';
                data.entry_types.forEach(type => {
                    journalTypeSelect.innerHTML += `<option value="${type.type}">${type.name}</option>`;
                });
            }
        } catch (error) {
            console.error('Error loading journal entry types:', error);
        }
    }

    async loadTabContent() {
        switch (this.currentTab) {
            case 'content':
                await this.loadContent();
                break;
            case 'journal':
                await this.loadJournalEntries();
                break;
            case 'learning-path':
                await this.loadLearningPaths();
                break;
            case 'goals':
                await this.loadGoals();
                break;
            case 'quiz':
                await this.loadQuizzes();
                break;
            case 'analytics':
                await this.loadAnalytics();
                break;
        }
    }

    async loadContent() {
        try {
            const contentType = document.getElementById('contentTypeFilter')?.value || '';
            const difficultyLevel = document.getElementById('difficultyFilter')?.value || '';
            
            let url = `${this.apiBase}/content?limit=50`;
            if (contentType) url += `&content_type=${contentType}`;
            if (difficultyLevel) url += `&difficulty_level=${difficultyLevel}`;
            
            const response = await fetch(url);
            const data = await response.json();
            
            this.displayContent(data.content);
        } catch (error) {
            console.error('Error loading content:', error);
            this.showError('Failed to load educational content');
        }
    }

    displayContent(content) {
        const container = document.getElementById('contentList');
        if (!container) return;
        
        if (content.length === 0) {
            container.innerHTML = '<div class="col-12"><div class="alert alert-info">No content found</div></div>';
            return;
        }
        
        container.innerHTML = content.map(item => `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card content-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title">${item.title}</h6>
                            <span class="badge bg-${this.getDifficultyColor(item.difficulty_level)} difficulty-badge">
                                ${item.difficulty_level.replace('_', ' ').toUpperCase()}
                            </span>
                        </div>
                        <p class="card-text text-muted small">${item.description || 'No description available'}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-${this.getContentTypeIcon(item.content_type)} me-1"></i>
                                ${item.content_type.replace('_', ' ').toUpperCase()}
                            </small>
                            ${item.content_duration ? `<small class="text-muted">${item.content_duration} min</small>` : ''}
                        </div>
                        <div class="mt-2">
                            ${item.tags ? item.tags.map(tag => `<span class="badge bg-secondary me-1">${tag}</span>`).join('') : ''}
                        </div>
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-sm btn-primary" onclick="educationalManager.viewContent('${item.id}')">
                            <i class="fas fa-eye me-1"></i>View
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="educationalManager.editContent('${item.id}')">
                            <i class="fas fa-edit me-1"></i>Edit
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async loadJournalEntries() {
        try {
            const response = await fetch(`${this.apiBase}/journal?limit=50`);
            const data = await response.json();
            
            this.displayJournalEntries(data.entries);
        } catch (error) {
            console.error('Error loading journal entries:', error);
            this.showError('Failed to load trading journal entries');
        }
    }

    displayJournalEntries(entries) {
        const container = document.getElementById('journalList');
        if (!container) return;
        
        if (entries.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No journal entries found</div>';
            return;
        }
        
        container.innerHTML = entries.map(entry => `
            <div class="card journal-entry mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title">${entry.title}</h6>
                        <span class="badge bg-${this.getEntryTypeColor(entry.entry_type)}">
                            ${entry.entry_type.replace('_', ' ').toUpperCase()}
                        </span>
                    </div>
                    <p class="card-text">${entry.content}</p>
                    <div class="row">
                        ${entry.symbol ? `<div class="col-md-3"><strong>Symbol:</strong> ${entry.symbol}</div>` : ''}
                        ${entry.trade_date ? `<div class="col-md-3"><strong>Date:</strong> ${new Date(entry.trade_date).toLocaleDateString()}</div>` : ''}
                        ${entry.pnl !== null ? `<div class="col-md-3"><strong>P&L:</strong> <span class="text-${entry.pnl >= 0 ? 'success' : 'danger'}">${entry.pnl.toFixed(2)}</span></div>` : ''}
                        ${entry.pnl_percent !== null ? `<div class="col-md-3"><strong>P&L%:</strong> <span class="text-${entry.pnl_percent >= 0 ? 'success' : 'danger'}">${entry.pnl_percent.toFixed(2)}%</span></div>` : ''}
                    </div>
                    ${entry.lessons_learned ? `<div class="mt-2"><strong>Lessons Learned:</strong> ${entry.lessons_learned}</div>` : ''}
                    ${entry.mistakes_made ? `<div class="mt-2"><strong>Mistakes Made:</strong> ${entry.mistakes_made}</div>` : ''}
                    ${entry.improvements ? `<div class="mt-2"><strong>Improvements:</strong> ${entry.improvements}</div>` : ''}
                    <div class="mt-2">
                        ${entry.tags ? entry.tags.map(tag => `<span class="badge bg-secondary me-1">${tag}</span>`).join('') : ''}
                    </div>
                </div>
                <div class="card-footer">
                    <button class="btn btn-sm btn-primary" onclick="educationalManager.viewJournalEntry('${entry.id}')">
                        <i class="fas fa-eye me-1"></i>View
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="educationalManager.editJournalEntry('${entry.id}')">
                        <i class="fas fa-edit me-1"></i>Edit
                    </button>
                </div>
            </div>
        `).join('');
    }

    async loadLearningPaths() {
        try {
            const response = await fetch(`${this.apiBase}/learning-paths?limit=50`);
            const data = await response.json();
            
            this.displayLearningPaths(data.paths);
        } catch (error) {
            console.error('Error loading learning paths:', error);
            this.showError('Failed to load learning paths');
        }
    }

    displayLearningPaths(paths) {
        const container = document.getElementById('learningPathList');
        if (!container) return;
        
        if (paths.length === 0) {
            container.innerHTML = '<div class="col-12"><div class="alert alert-info">No learning paths found</div></div>';
            return;
        }
        
        container.innerHTML = paths.map(path => `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card learning-path-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title">${path.name}</h6>
                            <span class="badge bg-${this.getDifficultyColor(path.difficulty_level)} difficulty-badge">
                                ${path.difficulty_level.replace('_', ' ').toUpperCase()}
                            </span>
                        </div>
                        <p class="card-text text-muted small">${path.description || 'No description available'}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-route me-1"></i>
                                Learning Path
                            </small>
                            ${path.estimated_duration ? `<small class="text-muted">${path.estimated_duration} hours</small>` : ''}
                        </div>
                        <div class="mt-2">
                            <div class="progress">
                                <div class="progress-bar" role="progressbar" style="width: ${path.progress || 0}%"></div>
                            </div>
                            <small class="text-muted">Progress: ${path.progress || 0}%</small>
                        </div>
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-sm btn-primary" onclick="educationalManager.viewLearningPath('${path.id}')">
                            <i class="fas fa-eye me-1"></i>View
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="educationalManager.editLearningPath('${path.id}')">
                            <i class="fas fa-edit me-1"></i>Edit
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async loadGoals() {
        try {
            const response = await fetch(`${this.apiBase}/goals?limit=50`);
            const data = await response.json();
            
            this.displayGoals(data.goals);
        } catch (error) {
            console.error('Error loading goals:', error);
            this.showError('Failed to load trading goals');
        }
    }

    displayGoals(goals) {
        const container = document.getElementById('goalsList');
        if (!container) return;
        
        if (goals.length === 0) {
            container.innerHTML = '<div class="col-12"><div class="alert alert-info">No goals found</div></div>';
            return;
        }
        
        container.innerHTML = goals.map(goal => `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card goal-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title">${goal.title}</h6>
                            <span class="badge bg-${this.getGoalStatusColor(goal.status)}">
                                ${goal.status.replace('_', ' ').toUpperCase()}
                            </span>
                        </div>
                        <p class="card-text text-muted small">${goal.description || 'No description available'}</p>
                        <div class="mb-2">
                            <strong>Target:</strong> ${goal.target_value} ${goal.unit}
                        </div>
                        <div class="mb-2">
                            <strong>Progress:</strong> ${goal.current_value || 0} / ${goal.target_value} ${goal.unit}
                        </div>
                        <div class="progress mb-2">
                            <div class="progress-bar" role="progressbar" style="width: ${(goal.current_value || 0) / goal.target_value * 100}%"></div>
                        </div>
                        <div class="row">
                            <div class="col-6">
                                <small class="text-muted">Start: ${new Date(goal.start_date).toLocaleDateString()}</small>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Target: ${new Date(goal.target_date).toLocaleDateString()}</small>
                            </div>
                        </div>
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-sm btn-primary" onclick="educationalManager.viewGoal('${goal.id}')">
                            <i class="fas fa-eye me-1"></i>View
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="educationalManager.editGoal('${goal.id}')">
                            <i class="fas fa-edit me-1"></i>Edit
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async loadQuizzes() {
        try {
            const response = await fetch(`${this.apiBase}/quiz?limit=50`);
            const data = await response.json();
            
            this.displayQuizzes(data.quizzes || []);
        } catch (error) {
            console.error('Error loading quizzes:', error);
            this.showError('Failed to load quizzes');
        }
    }

    displayQuizzes(quizzes) {
        const container = document.getElementById('quizList');
        if (!container) return;
        
        if (quizzes.length === 0) {
            container.innerHTML = '<div class="col-12"><div class="alert alert-info">No quizzes found</div></div>';
            return;
        }
        
        container.innerHTML = quizzes.map(quiz => `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card quiz-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title">${quiz.title}</h6>
                            <span class="badge bg-${this.getDifficultyColor(quiz.difficulty_level)} difficulty-badge">
                                ${quiz.difficulty_level.replace('_', ' ').toUpperCase()}
                            </span>
                        </div>
                        <p class="card-text text-muted small">${quiz.description || 'No description available'}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-question-circle me-1"></i>
                                ${quiz.questions ? quiz.questions.length : 0} Questions
                            </small>
                            ${quiz.time_limit ? `<small class="text-muted">${quiz.time_limit} min</small>` : ''}
                        </div>
                        <div class="mt-2">
                            <small class="text-muted">Passing Score: ${quiz.passing_score}%</small>
                        </div>
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-sm btn-primary" onclick="educationalManager.takeQuiz('${quiz.id}')">
                            <i class="fas fa-play me-1"></i>Take Quiz
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="educationalManager.viewQuiz('${quiz.id}')">
                            <i class="fas fa-eye me-1"></i>View
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async loadAnalytics() {
        try {
            const [learningResponse, journalResponse] = await Promise.all([
                fetch(`${this.apiBase}/analytics/learning`),
                fetch(`${this.apiBase}/analytics/journal`)
            ]);
            
            const learningData = await learningResponse.json();
            const journalData = await journalResponse.json();
            
            this.displayLearningAnalytics(learningData);
            this.displayJournalAnalytics(journalData);
        } catch (error) {
            console.error('Error loading analytics:', error);
            this.showError('Failed to load analytics');
        }
    }

    displayLearningAnalytics(data) {
        const container = document.getElementById('learningProgressChart');
        if (!container) return;
        
        // Create learning progress chart
        const ctx = document.createElement('canvas');
        container.appendChild(ctx);
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'In Progress', 'Not Started'],
                datasets: [{
                    data: [
                        data.completed_content || 0,
                        data.in_progress_content || 0,
                        data.not_started_content || 0
                    ],
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Learning Progress'
                    }
                }
            }
        });
    }

    displayJournalAnalytics(data) {
        const container = document.getElementById('journalAnalyticsChart');
        if (!container) return;
        
        // Create journal analytics chart
        const ctx = document.createElement('canvas');
        container.appendChild(ctx);
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Total Entries', 'Trade Entries', 'Analysis Entries', 'Lesson Entries'],
                datasets: [{
                    label: 'Journal Entries',
                    data: [
                        data.total_entries || 0,
                        data.trade_entries || 0,
                        data.analysis_entries || 0,
                        data.lesson_entries || 0
                    ],
                    backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Journal Analytics'
                    }
                }
            }
        });
    }

    async createContent() {
        try {
            const formData = {
                title: document.getElementById('contentTitle').value,
                content_type: document.getElementById('contentType').value,
                difficulty_level: document.getElementById('contentDifficulty').value,
                description: document.getElementById('contentDescription').value,
                content_url: document.getElementById('contentUrl').value,
                content_text: document.getElementById('contentText').value,
                content_duration: parseInt(document.getElementById('contentDuration').value) || null,
                tags: document.getElementById('contentTags').value.split(',').map(tag => tag.trim()).filter(tag => tag)
            };
            
            const response = await fetch(`${this.apiBase}/content/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                this.showSuccess('Educational content created successfully');
                bootstrap.Modal.getInstance(document.getElementById('createContentModal')).hide();
                document.getElementById('createContentForm').reset();
                this.loadContent();
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Failed to create content');
            }
        } catch (error) {
            console.error('Error creating content:', error);
            this.showError('Failed to create educational content');
        }
    }

    async createJournalEntry() {
        try {
            const formData = {
                title: document.getElementById('journalTitle').value,
                entry_type: document.getElementById('journalType').value,
                content: document.getElementById('journalContent').value,
                symbol: document.getElementById('journalSymbol').value || null,
                trade_date: document.getElementById('journalTradeDate').value || null,
                entry_price: parseFloat(document.getElementById('journalEntryPrice').value) || null,
                exit_price: parseFloat(document.getElementById('journalExitPrice').value) || null,
                quantity: parseInt(document.getElementById('journalQuantity').value) || null,
                pnl: null, // Calculate if entry_price and exit_price are provided
                pnl_percent: null, // Calculate if entry_price and exit_price are provided
                lessons_learned: document.getElementById('journalLessons').value || null,
                mistakes_made: document.getElementById('journalMistakes').value || null,
                improvements: document.getElementById('journalImprovements').value || null,
                tags: []
            };
            
            // Calculate P&L if both prices are provided
            if (formData.entry_price && formData.exit_price && formData.quantity) {
                formData.pnl = (formData.exit_price - formData.entry_price) * formData.quantity;
                formData.pnl_percent = ((formData.exit_price - formData.entry_price) / formData.entry_price) * 100;
            }
            
            const response = await fetch(`${this.apiBase}/journal/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                this.showSuccess('Trading journal entry created successfully');
                bootstrap.Modal.getInstance(document.getElementById('createJournalModal')).hide();
                document.getElementById('createJournalForm').reset();
                this.loadJournalEntries();
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Failed to create journal entry');
            }
        } catch (error) {
            console.error('Error creating journal entry:', error);
            this.showError('Failed to create trading journal entry');
        }
    }

    async createLearningPath() {
        try {
            const formData = {
                name: document.getElementById('pathName').value,
                description: document.getElementById('pathDescription').value,
                difficulty_level: document.getElementById('pathDifficulty').value,
                estimated_duration: parseInt(document.getElementById('pathDuration').value) || null,
                learning_objectives: document.getElementById('pathObjectives').value.split('\n').filter(obj => obj.trim())
            };
            
            const response = await fetch(`${this.apiBase}/learning-path/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                this.showSuccess('Learning path created successfully');
                bootstrap.Modal.getInstance(document.getElementById('createPathModal')).hide();
                document.getElementById('createPathForm').reset();
                this.loadLearningPaths();
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Failed to create learning path');
            }
        } catch (error) {
            console.error('Error creating learning path:', error);
            this.showError('Failed to create learning path');
        }
    }

    async createTradingGoal() {
        try {
            const formData = {
                title: document.getElementById('goalTitle').value,
                goal_type: document.getElementById('goalType').value,
                target_value: parseFloat(document.getElementById('goalTarget').value),
                unit: document.getElementById('goalUnit').value,
                start_date: document.getElementById('goalStartDate').value,
                target_date: document.getElementById('goalTargetDate').value,
                description: document.getElementById('goalDescription').value
            };
            
            const response = await fetch(`${this.apiBase}/goals/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                this.showSuccess('Trading goal created successfully');
                bootstrap.Modal.getInstance(document.getElementById('createGoalModal')).hide();
                document.getElementById('createGoalForm').reset();
                this.loadGoals();
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Failed to create trading goal');
            }
        } catch (error) {
            console.error('Error creating trading goal:', error);
            this.showError('Failed to create trading goal');
        }
    }

    async createQuiz() {
        try {
            const formData = {
                title: document.getElementById('quizTitle').value,
                description: document.getElementById('quizDescription').value,
                difficulty_level: document.getElementById('quizDifficulty').value,
                time_limit: parseInt(document.getElementById('quizTimeLimit').value) || null,
                passing_score: parseFloat(document.getElementById('quizPassingScore').value),
                questions: JSON.parse(document.getElementById('quizQuestions').value || '[]')
            };
            
            const response = await fetch(`${this.apiBase}/quiz/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                this.showSuccess('Quiz created successfully');
                bootstrap.Modal.getInstance(document.getElementById('createQuizModal')).hide();
                document.getElementById('createQuizForm').reset();
                this.loadQuizzes();
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Failed to create quiz');
            }
        } catch (error) {
            console.error('Error creating quiz:', error);
            this.showError('Failed to create quiz');
        }
    }

    applyFilters() {
        this.loadContent();
    }

    // Helper methods
    getDifficultyColor(level) {
        const colors = {
            'beginner': 'success',
            'intermediate': 'warning',
            'advanced': 'danger',
            'expert': 'dark'
        };
        return colors[level] || 'secondary';
    }

    getContentTypeIcon(type) {
        const icons = {
            'video': 'play-circle',
            'article': 'file-text',
            'tutorial': 'graduation-cap',
            'webinar': 'video',
            'podcast': 'microphone',
            'ebook': 'book',
            'course': 'chalkboard-teacher'
        };
        return icons[type] || 'file';
    }

    getEntryTypeColor(type) {
        const colors = {
            'trade': 'primary',
            'analysis': 'info',
            'lesson': 'success',
            'reflection': 'warning',
            'goal': 'secondary'
        };
        return colors[type] || 'secondary';
    }

    getGoalStatusColor(status) {
        const colors = {
            'active': 'success',
            'completed': 'primary',
            'paused': 'warning',
            'cancelled': 'danger'
        };
        return colors[status] || 'secondary';
    }

    showSuccess(message) {
        // Create and show success alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 3000);
    }

    showError(message) {
        // Create and show error alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }

    // Placeholder methods for view/edit actions
    viewContent(id) {
        console.log('View content:', id);
        // Implement content viewing
    }

    editContent(id) {
        console.log('Edit content:', id);
        // Implement content editing
    }

    viewJournalEntry(id) {
        console.log('View journal entry:', id);
        // Implement journal entry viewing
    }

    editJournalEntry(id) {
        console.log('Edit journal entry:', id);
        // Implement journal entry editing
    }

    viewLearningPath(id) {
        console.log('View learning path:', id);
        // Implement learning path viewing
    }

    editLearningPath(id) {
        console.log('Edit learning path:', id);
        // Implement learning path editing
    }

    viewGoal(id) {
        console.log('View goal:', id);
        // Implement goal viewing
    }

    editGoal(id) {
        console.log('Edit goal:', id);
        // Implement goal editing
    }

    takeQuiz(id) {
        console.log('Take quiz:', id);
        // Implement quiz taking
    }

    viewQuiz(id) {
        console.log('View quiz:', id);
        // Implement quiz viewing
    }
}

// Initialize educational manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.educationalManager = new EducationalManager();
});

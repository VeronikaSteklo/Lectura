class LecturaAssistant {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.currentFile = null;
    }

    initializeElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.browseBtn = document.getElementById('browseBtn');
        this.processBtn = document.getElementById('processBtn');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.resultSection = document.getElementById('resultSection');
        this.resultContent = document.getElementById('resultContent');
        this.errorAlert = document.getElementById('errorAlert');
        this.copyBtn = document.getElementById('copyBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.pasteHint = document.getElementById('pasteHint');
    }

    bindEvents() {
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        this.browseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.fileInput.click();
        });

        this.fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, this.highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, this.unhighlight, false);
        });

        this.uploadArea.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const file = dt.files[0];
            this.handleFileSelect(file);
        });

        document.addEventListener('paste', (e) => {
            this.handlePaste(e);
        });

        this.processBtn.addEventListener('click', () => {
            this.processImage();
        });

        this.copyBtn.addEventListener('click', () => {
            this.copyToClipboard();
        });

        this.downloadBtn.addEventListener('click', () => {
            this.downloadMarkdown();
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    highlight(e) {
        this.classList.add('dragover');
    }

    unhighlight(e) {
        this.classList.remove('dragover');
    }

    async handlePaste(e) {
        const items = e.clipboardData.items;

        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const file = items[i].getAsFile();
                if (file) {
                    this.handleFileSelect(file);
                    this.showNotification('Изображение вставлено из буфера обмена!');
                    break;
                }
            }
        }
    }

    handleFileSelect(file) {
        if (!file) return;

        const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
        if (!validTypes.includes(file.type)) {
            this.showError('Пожалуйста, выберите файл JPG или PNG');
            return;
        }

        this.currentFile = file;
        this.processBtn.disabled = false;

        this.uploadArea.innerHTML = `
            <i class="fas fa-check-circle fa-3x mb-3 text-success"></i>
            <h4>Выбран файл:</h4>
            <p class="text-primary fw-bold">${file.name}</p>
            <small class="text-muted">${(file.size / 1024 / 1024).toFixed(2)} MB</small>
            <div class="mt-3">
                <small class="text-muted">
                    <i class="fas fa-info-circle"></i> Подсказка: Вы можете также вставить изображение с помощью Ctrl+V
                </small>
            </div>
        `;
    }

    async processImage() {
        if (!this.currentFile) {
            this.showError('Пожалуйста, выберите файл');
            return;
        }

        this.hideError();
        this.showLoading();
        this.resultSection.classList.add('d-none');

        const formData = new FormData();
        formData.append('file', this.currentFile);

        try {
            const response = await fetch('/ocr', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                this.showResult(data.content);
                this.resultData = data;
            } else {
                this.showError(`Ошибка: ${data.detail || 'Неизвестная ошибка'}`);
            }
        } catch (error) {
            console.error('Ошибка:', error);
            this.showError('Ошибка соединения с сервером');
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        this.loadingIndicator.classList.remove('d-none');
        this.processBtn.disabled = true;
    }

    hideLoading() {
        this.loadingIndicator.classList.add('d-none');
        this.processBtn.disabled = false;
    }

    showResult(content) {
        this.resultContent.textContent = content;
        this.resultSection.classList.remove('d-none');
        this.resultSection.classList.add('fade-in');
    }

    showError(message) {
        this.errorAlert.textContent = message;
        this.errorAlert.classList.remove('d-none');
    }

    hideError() {
        this.errorAlert.classList.add('d-none');
    }

    copyToClipboard() {
        const text = this.resultContent.textContent;
        navigator.clipboard.writeText(text).then(() => {
            const originalText = this.copyBtn.innerHTML;
            this.copyBtn.innerHTML = '<i class="fas fa-check"></i> Скопировано!';
            setTimeout(() => {
                this.copyBtn.innerHTML = originalText;
            }, 2000);
        });
    }

    downloadMarkdown() {
        const content = this.resultContent.textContent;
        const filename = this.currentFile.name.replace(/\.[^/.]+$/, "") + '.md';

        const blob = new Blob([content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show position-fixed';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(notification);

        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.lectura = new LecturaAssistant();

    console.log('💡 Подсказка: Вы можете вставить изображение из буфера обмена с помощью Ctrl+V');
});

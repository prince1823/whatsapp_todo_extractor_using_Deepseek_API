document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const resultsDiv = document.getElementById('results');
    let todos = [];
    let completed = JSON.parse(localStorage.getItem('completedTodos')) || {};

    dropZone.addEventListener('click', () => fileInput.click());

    ['dragenter', 'dragover'].forEach(evt =>
        dropZone.addEventListener(evt, e => {
            e.preventDefault();
            dropZone.style.background = '#c5f0a4';
        }));

    ['dragleave', 'drop'].forEach(evt =>
        dropZone.addEventListener(evt, e => {
            e.preventDefault();
            dropZone.style.background = '';
        }));

    dropZone.addEventListener('drop', e => {
        fileInput.files = e.dataTransfer.files;
        processFile();
    });

    fileInput.addEventListener('change', processFile);

    function processFile() {
        if (!fileInput.files.length) return;

        const file = fileInput.files[0];
        if (!file.name.endsWith('.txt')) {
            alert('Please upload a .txt file');
            return;
        }

        resultsDiv.innerHTML = '<div class="empty-msg">Processing chat with AI...</div>';

        const formData = new FormData();
        formData.append('file', file);

        fetch('http://localhost:8000/extract', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                todos = JSON.parse(data.todos);
                renderTodos();
            } else {
                resultsDiv.innerHTML = `<div class="empty-msg">Error: ${data.error || 'Processing failed'}</div>`;
            }
        })
        .catch(error => {
            resultsDiv.innerHTML = `<div class="empty-msg">Error: ${error.message}</div>`;
        });
    }

    function renderTodos() {
        if (!todos.length) {
            resultsDiv.innerHTML = '<div class="empty-msg">No tasks found in chat</div>';
            return;
        }
    
        let myTasks = '';
        let assignedTasks = '';
        let myJson = [];
        let otherJson = [];
    
        todos.forEach(todo => {
            const todoId = `${todo.timestamp}-${todo.task.substring(0, 20)}`;
            const isCompleted = completed[todoId];
    
            const todoHTML = `
                <div class="todo-item ${isCompleted ? 'completed' : ''}" data-id="${todoId}">
                    <input type="checkbox" ${isCompleted ? 'checked' : ''}>
                    <div class="todo-text">${todo.task}</div>
                    <div class="todo-time">🕒 ${todo.timestamp}</div>
                </div>
            `;
    
            if (todo.recipient.toLowerCase() === 'me') {
                myTasks += todoHTML;
                myJson.push(todo);
            } else {
                assignedTasks += todoHTML;
                otherJson.push(todo);
            }
        });
    
        resultsDiv.innerHTML = `
            <div class="todo-section">
                <h2>📋 Tasks for Me</h2>
                ${myTasks || '<div class="empty-msg">No tasks assigned to you</div>'}
                <button class="download-btn" id="downloadMine">⬇ Download Tasks for Me</button>
            </div>
            <div class="todo-section">
                <h2>👥 Tasks for Others</h2>
                ${assignedTasks || '<div class="empty-msg">No tasks assigned to others</div>'}
                <button class="download-btn" id="downloadOthers">⬇ Download Tasks for Others</button>
            </div>
        `;
    
        document.querySelectorAll('.todo-item input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', function () {
                const todoId = this.parentElement.dataset.id;
                if (this.checked) {
                    completed[todoId] = true;
                } else {
                    delete completed[todoId];
                }
                localStorage.setItem('completedTodos', JSON.stringify(completed));
                this.parentElement.classList.toggle('completed');
            });
        });
    
        document.getElementById('downloadMine').addEventListener('click', () => downloadJSON(myJson, "my_tasks"));
        document.getElementById('downloadOthers').addEventListener('click', () => downloadJSON(otherJson, "assigned_tasks"));
    }
    
    function downloadJSON(data, filename) {
        const strippedData = data.map(todo => {
            const { priority, ...rest } = todo;
            return rest;
        });
    
        const blob = new Blob([JSON.stringify(strippedData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}_${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
    
});

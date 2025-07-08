document.addEventListener('DOMContentLoaded', function() {
    // Установка текущего года в футере
    document.getElementById('currentYear').textContent = new Date().getFullYear();
    
    // Обновление статуса бота
    updateStatus();
    
    // Обновляем статус каждую минуту
    setInterval(updateStatus, 60000);
    
    // Загружаем данные API, если на странице есть элемент api-status
    if (document.getElementById('api-status')) {
        fetchApiStatus();
    }
});

function updateStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            const now = new Date(data.server_time);
            const startTime = new Date(data.start_time);
            const endTime = new Date(data.end_time);
            
            const statusCard = document.getElementById('statusCard');
            if (statusCard) {
                const statusIcon = statusCard.querySelector('.status-icon i');
                const statusText = statusCard.querySelector('.status-info h2');
                const progressBar = document.getElementById('progressBar');
                
                // Форматируем время
                const formatTime = (seconds) => {
                    if (seconds <= 0) return "00:00:00";
                    
                    const hrs = Math.floor(seconds / 3600);
                    const mins = Math.floor((seconds % 3600) / 60);
                    const secs = Math.floor(seconds % 60);
                    
                    return [
                        hrs.toString().padStart(2, '0'),
                        mins.toString().padStart(2, '0'),
                        secs.toString().padStart(2, '0')
                    ].join(':');
                };
                
                // Обновляем оставшееся время
                const remainingElement = document.getElementById('remainingTime');
                if (remainingElement) {
                    remainingElement.textContent = formatTime(data.remaining_seconds);
                }
                
                // Проверяем статус бота
                if (data.status === 'running') {
                    const totalSeconds = (endTime - startTime) / 1000;
                    const progress = ((totalSeconds - data.remaining_seconds) / totalSeconds) * 100;
                    
                    statusCard.style.borderLeft = '5px solid var(--success)';
                    statusIcon.className = 'fas fa-check-circle';
                    statusIcon.style.color = 'var(--success)';
                    statusText.textContent = 'Бот работает';
                    statusText.style.color = 'var(--success)';
                    
                    progressBar.style.width = `${Math.min(progress, 100)}%`;
                    progressBar.style.backgroundColor = progress > 80 ? 'var(--danger)' : 'var(--success)';
                } else {
                    statusCard.style.borderLeft = '5px solid var(--danger)';
                    statusIcon.className = 'fas fa-times-circle';
                    statusIcon.style.color = 'var(--danger)';
                    statusText.textContent = 'Бот не работает';
                    statusText.style.color = 'var(--danger)';
                    
                    progressBar.style.width = '100%';
                    progressBar.style.backgroundColor = 'var(--danger)';
                }
            }
        })
        .catch(error => console.error('Error fetching status:', error));
}

function fetchApiStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            const apiStatusElement = document.getElementById('api-status');
            apiStatusElement.innerHTML = `
                <pre>${JSON.stringify(data, null, 2)}</pre>
                <p>Вы можете использовать этот API для интеграции с другими системами.</p>
            `;
        })
        .catch(error => {
            document.getElementById('api-status').innerHTML = `
                <p class="error">Ошибка при загрузке API данных: ${error.message}</p>
            `;
        });
                                                                   }

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('certForm');
    const resultsDiv = document.getElementById('results');
    const resultContent = document.getElementById('resultContent');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        if (validateForm()) {
            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries());
            
            // 显示加载信息
            resultContent.innerHTML = '正在生成证书，请稍候...';
            resultsDiv.style.display = 'block';

            // 发送API请求生成证书
            fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(files => {
                displayResults(files);
            })
            .catch(error => {
                console.error('Error:', error);
                let errorMessage = '生成证书时发生错误: ';
                if (error.error) {
                    errorMessage += error.error;
                } else {
                    errorMessage += JSON.stringify(error);
                }
                resultContent.innerHTML = `<p style="color: red;">${errorMessage}</p>`;
                resultsDiv.style.display = 'block';
            });
        }
    });

    function validateForm() {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('error');
            } else {
                field.classList.remove('error');
            }
        });

        const durationDays = document.getElementById('durationDays');
        if (parseInt(durationDays.value) <= 0) {
            isValid = false;
            durationDays.classList.add('error');
        } else {
            durationDays.classList.remove('error');
        }

        return isValid;
    }

    function displayResults(files) {
        let resultText = "证书生成成功！\n\n";
        resultText += "生成的文件：\n";
        
        let downloadLinks = '';
        for (const [key, value] of Object.entries(files)) {
            resultText += `${key}: ${value}\n`;
            downloadLinks += `<a href="/download/${value}" download="${value}">下载 ${value}</a><br>`;
        }

        resultContent.innerHTML = `<pre>${resultText}</pre>${downloadLinks}`;
        resultsDiv.style.display = 'block';
    }
});
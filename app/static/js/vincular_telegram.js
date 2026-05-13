document.addEventListener('DOMContentLoaded', () => {
    const copyBtn = document.getElementById('copyBtn');
    const syncToken = document.getElementById('syncToken');
    const checkBtn = document.getElementById('checkStatusBtn');

    // Función para copiar el código al portapapeles
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const textToCopy = syncToken.innerText;
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalEmoji = copyBtn.innerText;
                copyBtn.innerText = '✅';
                setTimeout(() => {
                    copyBtn.innerText = originalEmoji;
                }, 2000);
            });
        });
    }

    // Botón de verificar estado 
    if (checkBtn) {
        checkBtn.addEventListener('click', () => {
            checkBtn.innerText = 'Verificando...';
            
            window.location.reload();
        });
    }
});
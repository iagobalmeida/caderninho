
document.querySelectorAll('input[type="reset"]').forEach(inputReset => {
    inputReset.addEventListener('click', (e) => {
            Array.from(inputReset.form.elements).forEach(element => {
                if (element.type === 'search' || element.type === 'text' || element.type === 'textarea' || element.type === 'date') {
                element.removeAttribute('value');
                element.value = '';
            } else if (element.type === 'checkbox' || element.type === 'radio') {
                element.checked = false;
            } else if (element.tagName === 'SELECT') {
                element.selectedIndex = -1;
            }
        });
        inputReset.form.submit();
    });
});
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener("show.bs.modal", (e) => {
        if(e.relatedTarget.tagName == 'INPUT' && e.type == 'checkbox') {
            e.preventDefault();
            return
        }
        const payload_json = e.relatedTarget.getAttribute('data-bs-payload');
        const payload = JSON.parse(payload_json);
        if(!payload) return;
        Object.keys(payload).forEach(payload_key => {
            modal.querySelectorAll(`input[name="${payload_key}"]`).forEach(el => {
                if(el.type == 'datetime-local') {
                    const value = payload[payload_key].substring(0, 16);
                    el.value = value;
                } else {
                    el.value = payload[payload_key];
                }
            })
            modal.querySelectorAll(`select[name="${payload_key}"]`).forEach(el => {
                el.value = payload[payload_key];
            })
            modal.querySelectorAll('[data-bs-payload]').forEach(el => {
                el.setAttribute('data-bs-payload', payload_json);
            })
        });
    });
});
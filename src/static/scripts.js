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
        let payload_json = e.relatedTarget.getAttribute('data-bs-payload');
        if(!payload_json) {
            payload_json = e.relatedTarget.parentElement.getAttribute('data-bs-payload');
        }
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

const inputSelecionados = document.querySelectorAll('input[name="selecionados_ids"]');
let checkboxesLastValue = true;
const updateDeleteAllButton = () => {
    const checkeds = Array.from(document.querySelectorAll('td input[type="checkbox"]:checked')).map(el => el.getAttribute('data-id'));
    if(checkeds.length) {
        document.querySelector('#btn-apagar-selecionados').removeAttribute("disabled")
    } else {
        document.querySelector('#btn-apagar-selecionados').setAttribute("disabled", true)
    }
    if(inputSelecionados) inputSelecionados.forEach(el => el.value = checkeds);
}

document.querySelectorAll('td input[type="checkbox"]').forEach(el => {
        el.style.pointerEvents = 'none';
        el.addEventListener('click', (e) => e.preventDefault());

        el.closest('td').addEventListener('mousedown', (ev) => {
            el.checked = !el.checked;
            checkboxesLastValue = el.checked;
            updateDeleteAllButton();
        });

        el.closest('td').addEventListener('mouseover', (ev) => {
            if(ev.buttons) {
                el.checked = checkboxesLastValue;
                updateDeleteAllButton();
            }
        });

        el.closest('td').addEventListener('mouseleave', (ev) => {
            if (window.getSelection) {
                if (window.getSelection().empty) {  // Chrome
                    window.getSelection().empty();
                } else if (window.getSelection().removeAllRanges) {  // Firefox
                    window.getSelection().removeAllRanges();
                }
            } else if (document.selection) {  // IE?
                document.selection.empty();
            }
        });
    }
);

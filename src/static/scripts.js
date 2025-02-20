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
                }
                else if(el.type == 'checkbox') {
                    el.checked = Boolean(payload[payload_key]);
                } else {
                    el.value = payload[payload_key];
                }
            });
            modal.querySelectorAll(`select[name="${payload_key}"]`).forEach(el => {
                el.value = payload[payload_key];
            });
            modal.querySelectorAll('[data-bs-payload]').forEach(el => {
                el.setAttribute('data-bs-payload', payload_json);
            });
            // 'action': 'http://google.com.br' => <form action="http://google.com.br">
            if(payload_key == 'action') {
                modal.querySelector('form').setAttribute('action', payload[payload_key]);
            }
            // '#test':'foo' => <... id="test">foo</...>
            // '.test':'foo' => <... class="test">foo</...>
            if(payload_key.includes('#') || payload_key.includes('.')){
                const target = modal.querySelector(payload_key)
                if(target) {
                    target.innerHTML = payload[payload_key];
                }
            }
        });
    });
});

const inputSelecionados = document.querySelectorAll('input[name="selecionados_ids"]');
let checkboxesLastValue = true;
const updateDeleteAllButton = () => {
    const checkeds = Array.from(document.querySelectorAll('td input[type="checkbox"]:checked')).map(el => el.getAttribute('data-id'));
    if(checkeds.length) {
        document.querySelectorAll('#btn-excluir-selecionados').forEach(el => {
            el.removeAttribute('disabled');
        })
        document.querySelectorAll('[data-depends-selected="true"]').forEach(el => {
            el.removeAttribute('disabled');
        })
    } else {
        document.querySelectorAll('#btn-excluir-selecionados').forEach(el => {
            el.setAttribute("disabled", true);
        })
        document.querySelectorAll('[data-depends-selected="true"]').forEach(el => {
            el.setAttribute("disabled", true);
        })
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


window.addEventListener('load', () => {
    const alertaSobreEssaPagina = document.querySelector('#alerta-sobre-essa-pagina');
    if(!alertaSobreEssaPagina) return;

    const alertaSobreEssaPaginaClose = alertaSobreEssaPagina.querySelector('a[data-bs-dismiss]');

    let alertaSobreIgnorados = [];

    try {
        alertaSobreIgnorados = JSON.parse(localStorage.getItem('alertaSobreIgnorados')) || [];
    } catch {
        console.log('Falha ao carregar avisos lidos');
    }
    const currentPage = window.location.href.split('/app/')[1].split('/')[0];

    if(!alertaSobreIgnorados.includes(currentPage)) {
        alertaSobreEssaPagina.classList.remove('d-none');
    }
    alertaSobreEssaPaginaClose.addEventListener('click', (e) => {
        alertaSobreIgnorados.push(currentPage)
        localStorage.setItem('alertaSobreIgnorados', JSON.stringify(alertaSobreIgnorados))
    });
})

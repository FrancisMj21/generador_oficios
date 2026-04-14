let seleccionados = [];

function actualizarSeleccionadosUI() {
    const count = seleccionados.length;
    const text = `(${count})`;
    const countNode = document.getElementById("seleccionadosCount");
    const buttonCountNode = document.getElementById("seleccionadosCountButton");
    const selectAll = document.getElementById("selectAll");
    const rowChecks = document.querySelectorAll('#tablaDocumentos input[type="checkbox"]');

    if (countNode) {
        countNode.textContent = text;
    }

    if (buttonCountNode) {
        buttonCountNode.textContent = text;
    }

    if (selectAll) {
        selectAll.checked = rowChecks.length > 0 && seleccionados.length === rowChecks.length;
    }
}

function toggleSeleccion(id, checked) {
    if (checked) {
        if (!seleccionados.includes(id)) {
            seleccionados.push(id);
        }
    } else {
        seleccionados = seleccionados.filter((item) => item !== id);
    }

    actualizarSeleccionadosUI();
}

function toggleTodos(checked) {
    const checkboxes = document.querySelectorAll('#tablaDocumentos input[type="checkbox"]');
    seleccionados = [];

    checkboxes.forEach((checkbox) => {
        checkbox.checked = checked;
        if (checked) {
            seleccionados.push(checkbox.value);
        }
    });

    actualizarSeleccionadosUI();
}

function eliminar(id) {
    if (confirm("Eliminar registro?")) {
        fetch("/eliminar/" + id, {
            method: "DELETE"
        }).then(() => location.reload());
    }
}

function ver(id) {
    window.open("/ver/" + id, "_blank");
}

function descargar(id) {
    window.location = "/descargar/" + id;
}

function generarSeleccionados() {
    if (!seleccionados.length) {
        alert("Selecciona al menos un registro para generar.");
        return;
    }

    fetch("/generar", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            ids: seleccionados
        })
    })
        .then((res) => res.json())
        .then(() => location.reload());
}

function descargarZIP() {
    if (!seleccionados.length) {
        alert("Selecciona al menos un registro para descargar el ZIP.");
        return;
    }

    window.location = "/descargar_zip?ids=" + encodeURIComponent(seleccionados.join(","));
}

document.addEventListener("DOMContentLoaded", () => {
    actualizarSeleccionadosUI();
});

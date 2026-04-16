let seleccionados = [];

function normalizarTipoPersona(valor) {
    return String(valor || "").trim().toUpperCase();
}

function obtenerTipoSeleccionado() {
    const seleccionado = document.querySelector('input[name="tipo_persona_id"]:checked');
    if (!seleccionado) {
        return "";
    }
    return normalizarTipoPersona(seleccionado.dataset.tipoNombre);
}

function obtenerSexoSeleccionado() {
    const seleccionado = document.querySelector('input[name="sexo"]:checked');
    return String(seleccionado?.value || "masculino").toLowerCase();
}

function construirCargoDesdeDatos(tipoPersona, sexo, condicion) {
    const tipo = normalizarTipoPersona(tipoPersona);
    const sexoNormalizado = String(sexo || "masculino").trim().toLowerCase();
    const condicionNormalizada = String(condicion || "").trim().toUpperCase();

    const mapaBase = {
        DOCENTE: "PROFESOR",
        AUXILIAR: "AUXILIAR DE EDUCACION",
        "AUXILIAR DE EDUCACION": "AUXILIAR DE EDUCACION",
        ADMINISTRATIVO: "ADMINISTRATIVO"
    };

    const mapaFemenino = {
        PROFESOR: "PROFESORA",
        ADMINISTRATIVO: "ADMINISTRATIVA"
    };

    const condicionesFemeninas = {
        NOMBRADO: "NOMBRADA",
        CONTRATADO: "CONTRATADA"
    };

    const tipoBase = mapaBase[tipo] || tipo;
    const tipoFinal = sexoNormalizado === "femenino"
        ? (mapaFemenino[tipoBase] || tipoBase)
        : tipoBase;
    const condicionFinal = sexoNormalizado === "femenino"
        ? (condicionesFemeninas[condicionNormalizada] || condicionNormalizada)
        : condicionNormalizada;

    return [tipoFinal, condicionFinal].filter(Boolean).join(" ").trim();
}

function obtenerCargoAutomatico() {
    const tipo = obtenerTipoSeleccionado();
    const sexo = obtenerSexoSeleccionado();
    const condicionSeleccionada = document.querySelector('input[name="condicion_id"]:checked');
    const condicion = condicionSeleccionada
        ? condicionSeleccionada.parentElement?.textContent?.trim() || ""
        : "";

    return construirCargoDesdeDatos(tipo, sexo, condicion);
}

function actualizarCargoActual() {
    const campoCargo = document.getElementById("cargo_actual");
    if (!campoCargo) {
        return;
    }

    campoCargo.value = obtenerCargoAutomatico();
}

function escaparHtml(valor) {
    return String(valor ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function formatearTextoSaltos(valor) {
    return escaparHtml(valor || "-").replace(/\n/g, "<br>");
}

function obtenerPersonaPorId(id) {
    const filas = document.querySelectorAll("#tablaDocumentos tr");

    for (const fila of filas) {
        const checkbox = fila.querySelector('input[type="checkbox"][value]');
        const dataCell = fila.querySelector("[data-persona]");
        if (!checkbox || !dataCell || checkbox.value !== String(id)) {
            continue;
        }

        try {
            return JSON.parse(dataCell.dataset.persona);
        } catch (error) {
            console.error("No se pudo leer data-persona", error);
            return null;
        }
    }

    return null;
}

function construirPreviewDocumento(persona) {
    const nombre = escaparHtml(persona.nombre || "");
    const cargo = escaparHtml(
        construirCargoDesdeDatos(persona.tipo_persona || "", persona.sexo || "", persona.condicion || "")
    );
    const centro = escaparHtml(persona.centro_trabajo || "");
    const direccion = escaparHtml(persona.direccion || "");
    const provincia = escaparHtml(persona.provincia || "TACNA");
    const telefono = escaparHtml(persona.telefono || "");
    const correo = escaparHtml(persona.correo || "");
    const solicita = escaparHtml(persona.solicita || "");
    const periodos = (persona.periodos || "")
        .split(/\r?\n/)
        .map((item) => item.trim())
        .filter(Boolean);

    const periodosHtml = periodos.length
        ? `
            <div class="doc-preview-periodos">
                <div class="doc-preview-periodos-title">Periodo(s)</div>
                ${periodos.map((item) => `<div class="doc-preview-periodo">- ${escaparHtml(item)}</div>`).join("")}
            </div>
        `
        : "";

    return `
        <article class="doc-preview">
            <header class="doc-preview-header">
                <div class="doc-preview-brand">
                    <div class="doc-preview-shield">TACNA</div>
                    <div class="doc-preview-ugel">UGEL TACNA</div>
                </div>
                <div class="doc-preview-motto">
                    <p>"Decenio de la igualdad de oportunidades para mujeres y hombres"</p>
                    <p>"Año de la recuperación y consolidación de la educación pública"</p>
                </div>
            </header>

            <div class="doc-preview-rule"></div>
            <p class="doc-preview-date">Tacna, ${new Date().toLocaleDateString("es-PE")}</p>
            <p class="doc-preview-code"><span>OFICIO N°</span>      -UFESC-URRHH/UGEL.T/GOB.REG.TACNA</p>

            <section class="doc-preview-meta">
                <p><strong>SEÑOR:</strong></p>
                <p><strong>${nombre}</strong></p>
                <p><strong>${cargo.toUpperCase()}</strong></p>
                <p><strong>${centro.toUpperCase()}</strong></p>
                <p><strong>DIRECCIÓN:</strong> ${direccion}</p>
                <p><strong>Tacna/Tacna:</strong> ${provincia}</p>
                <p><strong>Teléfono:</strong> ${telefono}</p>
                <p><strong>Correo:</strong> ${correo}</p>
            </section>

            <section class="doc-preview-topics">
                <p><strong>ASUNTO:</strong> FORMULO RESPUESTA</p>
                <p><strong>REFERENCIA:</strong> CUD. N° 1016344/23/02/2026</p>
            </section>

            <div class="doc-preview-rule"></div>

            <section class="doc-preview-body">
                <p>
                    Tengo el agrado de dirigirme a usted, para expresarle mi cordial saludo y a la vez brindar
                    la debida atención al documento de la referencia, mediante el cual solicita ${solicita}.
                </p>
                <p>
                    Al respecto, se deberá tener presente que el literal l) del artículo 41° de la Ley N° 29944,
                    Ley de Reforma Magisterial, reconoce el derecho al cómputo del tiempo de servicios efectivos;
                    asimismo, para el reconocimiento por tiempo de servicios se consideran los periodos prestados
                    bajo los regímenes señalados por la normativa vigente, incluyendo servicios en condición de contratado.
                </p>
                <p>
                    De acuerdo con la R.V.M. N° 112-2023-MINEDU, se regulan los procedimientos técnicos del
                    Escalafón Magisterial, precisándose que el profesor puede solicitar el reconocimiento del tiempo
                    de servicios prestados en instituciones educativas públicas adjuntando sus resoluciones y documentos
                    de sustento correspondientes.
                </p>
                <p>
                    Por ello, luego de la revisión del expediente, se advierte que aún falta documentación sustentatoria
                    para continuar con el procedimiento administrativo. Bajo su responsabilidad, deberá efectuar la
                    subsanación correspondiente.
                </p>
                ${periodosHtml}
                <p>
                    Sin otro particular, hago propicia la oportunidad para reiterarle las muestras de mi especial
                    consideración y estima personal.
                </p>
            </section>

            <footer class="doc-preview-signature">
                <p>Atentamente,</p>
                <p><strong>GOBIERNO REGIONAL DE TACNA</strong></p>
                <p>__________________________________________</p>
                <p><strong>ABOG. EDICA CARINA CANQUI ATENCIO</strong></p>
                <p><strong>JEFE DE LA UNIDAD DE RECURSOS HUMANOS</strong></p>
                <p><strong>UGEL TACNA</strong></p>
                <div class="doc-preview-mini">
                    <p>ECCA/UGRH</p>
                    <p>MLBR/AAJPG</p>
                </div>
            </footer>
        </article>
    `;
}

function obtenerPersonasSeleccionadas() {
    const filas = document.querySelectorAll("#tablaDocumentos tr");
    const personas = [];

    filas.forEach((fila) => {
        const checkbox = fila.querySelector('input[type="checkbox"][value]');
        const dataCell = fila.querySelector("[data-persona]");
        if (!checkbox || !dataCell) {
            return;
        }

        if (!seleccionados.includes(checkbox.value)) {
            return;
        }

        try {
            personas.push(JSON.parse(dataCell.dataset.persona));
        } catch (error) {
            console.error("No se pudo leer data-persona", error);
        }
    });

    return personas;
}

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
    const persona = obtenerPersonaPorId(id);
    const modal = document.getElementById("previewModal");
    const body = document.getElementById("previewBody");
    const subtitle = document.getElementById("previewSubtitle");
    const downloadBtn = document.getElementById("previewDownloadBtn");

    if (!persona || !modal || !body || !subtitle || !downloadBtn) {
        window.location = "/descargar/" + id;
        return;
    }

    body.innerHTML = construirPreviewDocumento(persona);
    subtitle.textContent = persona.nombre || "Documento administrativo";
    downloadBtn.onclick = () => descargar(id);
    modal.hidden = false;
    document.body.classList.add("modal-open");
}

function cerrarPreview() {
    const modal = document.getElementById("previewModal");
    const body = document.getElementById("previewBody");

    if (!modal || modal.hidden) {
        return;
    }

    modal.hidden = true;
    document.body.classList.remove("modal-open");

    if (body) {
        body.innerHTML = "";
    }
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
            ids: seleccionados,
            personas: obtenerPersonasSeleccionadas()
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
    actualizarCargoActual();

    document.querySelectorAll('input[name="tipo_persona_id"]').forEach((input) => {
        input.addEventListener("change", actualizarCargoActual);
    });

    document.querySelectorAll('input[name="sexo"]').forEach((input) => {
        input.addEventListener("change", actualizarCargoActual);
    });

    document.querySelectorAll('input[name="condicion_id"]').forEach((input) => {
        input.addEventListener("change", actualizarCargoActual);
    });
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        cerrarPreview();
    }
});

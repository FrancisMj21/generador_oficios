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
    const condicion = condicionSeleccionada?.nextElementSibling?.textContent.trim() || "";

    return construirCargoDesdeDatos(tipo, sexo, condicion);
}

function actualizarCargoActual() {
    const campoCargo = document.getElementById("cargo_actual");
    if (!campoCargo) {
        return;
    }

    campoCargo.readOnly = true;
    campoCargo.placeholder = "Se completa automáticamente";
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

function obtenerOficioPorId(id) {
    const filas = document.querySelectorAll("#tablaDocumentos tr");

    for (const fila of filas) {
        const checkbox = fila.querySelector('input[type="checkbox"][value]');
        const dataCell = fila.querySelector("[data-oficio]");
        if (!checkbox || !dataCell || checkbox.value !== String(id)) {
            continue;
        }

        try {
            return JSON.parse(dataCell.dataset.oficio);
        } catch (error) {
            console.error("No se pudo leer data-oficio", error);
            return null;
        }
    }

    return null;
}

function construirPreviewDocumento(oficio) {
    const persona = oficio; // Fields copied from persona in backend
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

function obtenerOficiosSeleccionados() {
    const filas = document.querySelectorAll("#tablaDocumentos tr");
    const oficios = [];

    filas.forEach((fila) => {
        const checkbox = fila.querySelector('input[type="checkbox"][value]');
        const dataCell = fila.querySelector("[data-oficio]");
        if (!checkbox || !dataCell) {
            return;
        }

        if (!seleccionados.includes(checkbox.value)) {
            return;
        }

        try {
            oficios.push(JSON.parse(dataCell.dataset.oficio));
        } catch (error) {
            console.error("No se pudo leer data-oficio", error);
        }
    });

    return oficios;
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

function toggleTodosForm(checked) {
    // Form select all - currently no checkboxes in form, stub for future
    console.log("Form select all toggled:", checked);
}

function eliminar(id) {
    if (confirm("Eliminar registro?")) {
        fetch("/eliminar/" + id, {
            method: "DELETE"
        }).then(() => location.reload());
    }
}

function ver(id){
    window.open("/descargar/" + id, "_blank");
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
            oficios: obtenerOficiosSeleccionados()
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

function agregarPeriodo(){
    const contenedor = document.getElementById("contenedor_periodos")

    const fila = document.querySelector(".periodo-fila")

    const nueva = fila.cloneNode(true)

    nueva.querySelectorAll("input").forEach(i => i.value = "")
    nueva.querySelectorAll("select").forEach(s => s.selectedIndex = 0)

    contenedor.appendChild(nueva)
    updatePeriodos();
}

function eliminarPeriodo(btn){

    const contenedor = document.getElementById("contenedor_periodos")

    const filas = contenedor.querySelectorAll(".periodo-fila")

    if(filas.length === 1){
        alert("Debe existir al menos un periodo")
        return
    }

    btn.parentElement.remove()
    updatePeriodos();
}

function updatePeriodos() {
    const contenedor = document.getElementById("contenedor_periodos");
    if (!contenedor) return true;

    const filas = contenedor.querySelectorAll(".periodo-fila");
    const periodos = [];

    filas.forEach(fila => {
        const selects = fila.querySelectorAll("select");
        const inputs = fila.querySelectorAll("input[type='number']");
        const mesInicioSel = selects[0];
        const anioInicioInput = inputs[0];
        const mesFinSel = selects[1];
        const anioFinInput = inputs[1];

        const mesInicio = mesInicioSel ? mesInicioSel.value : "";
        const anioInicio = anioInicioInput ? anioInicioInput.value : "";
        const mesFin = mesFinSel ? mesFinSel.value : "";
        const anioFin = anioFinInput ? anioFinInput.value : "";

        if (mesInicio && anioInicio && mesFin && anioFin) {
            const periodo = `${mesInicio}-${anioInicio} - ${mesFin}-${anioFin}`;
            periodos.push(periodo);
        }
    });

    const hiddenPeriodos = document.getElementById("periodos");
    if (hiddenPeriodos) {
        hiddenPeriodos.value = periodos.join("\\n");
    }

    // Return true if at least one valid period or field not required
    return periodos.length > 0 || true;
}

document.addEventListener("DOMContentLoaded", () => {
    updatePeriodos(); // Initial

    actualizarSeleccionadosUI();
    actualizarCargoActual();

    const camposCargo = [
        ...document.querySelectorAll('input[name="tipo_persona_id"]'),
        ...document.querySelectorAll('input[name="sexo"]'),
        ...document.querySelectorAll('input[name="condicion_id"]')
    ];

    camposCargo.forEach(el => {
        el.addEventListener("change", actualizarCargoActual);
    });

    // Hook period field changes
    const contenedor = document.getElementById("contenedor_periodos");
    if (contenedor) {
        contenedor.addEventListener("change", updatePeriodos);
        contenedor.addEventListener("input", updatePeriodos);
    }
})

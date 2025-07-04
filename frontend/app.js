let mediaRecorder;
let audioChunks = [];
let grabacionInterval;
let segundosGrabados = 0;

document.addEventListener('DOMContentLoaded', () => {
    // Referencias a elementos del DOM
    const recordBtn = document.getElementById("record");
    const stopBtn = document.getElementById("stop");
    const player = document.getElementById("player");
    const transcripcionTextarea = document.getElementById("transcripcion");
    const guardarBtn = document.getElementById("guardar");
    const estado = document.getElementById("estado");
    const clienteSelect = document.getElementById("cliente");

    // --- Función auxiliar para actualizar el selector ---
    function actualizarClienteSelect(clientes) {
        const select = document.querySelector("#cliente");

        if (select.tomselect) {
            select.tomselect.destroy();
        }

        select.innerHTML = '<option value="">Seleccioná un cliente</option>';

        clientes.forEach(c => {
            const option = document.createElement("option");
            option.value = c;
            option.textContent = c;
            select.appendChild(option);
        });

        new TomSelect("#cliente", {
            create: false,
            sortField: {
                field: "text",
                direction: "asc"
            },
            placeholder: "Escribí para buscar un cliente"
        });
    }

    // --- Función para cargar clientes ---
    async function cargarClientes() {
        const cache = localStorage.getItem("clientes_crm");
        let clientes = [];

        if (cache) {
            clientes = JSON.parse(cache);
            actualizarClienteSelect(clientes);
            estado.textContent = "📴 Clientes cargados desde caché local";
        } else {
            estado.textContent = "⏳ Buscando clientes...";
        }

        if (navigator.onLine) {
            try {
                const res = await fetch("https://transcriptor-backend-jw83.onrender.com/clientes_crm/");
                if (!res.ok) throw new Error("Respuesta no válida");

                const nuevosClientes = await res.json();
                localStorage.setItem("clientes_crm", JSON.stringify(nuevosClientes));
                actualizarClienteSelect(nuevosClientes);
                estado.textContent = "✅ Clientes actualizados desde el servidor";
            } catch (err) {
                console.warn("❌ No se pudo actualizar clientes desde el backend:", err);
            }
        }
    }

    // 🎙️ Iniciar grabación
    recordBtn.onclick = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = e => {
                audioChunks.push(e.data);
            };

            mediaRecorder.onstop = async () => {
    clearInterval(grabacionInterval);
    const blob = new Blob(audioChunks, { type: "audio/wav" });
    player.src = URL.createObjectURL(blob);

    guardarBtn.disabled = false;
    estado.textContent = "🎙️ Grabación finalizada. Escribí tu comentario.";
};

// ✅ Esto estaba mal indentado antes:
mediaRecorder.start();
recordBtn.disabled = true;
stopBtn.disabled = false;

// Iniciar contador visual
segundosGrabados = 0;
estado.textContent = `🎙️ Grabando... 0s`;
grabacionInterval = setInterval(() => {
    segundosGrabados++;
    estado.textContent = `🎙️ Grabando... ${segundosGrabados}s`;
}, 1000);
        } catch (error) {
            console.error("Error al acceder al micrófono:", error);
            estado.textContent = "❌ Error: Necesitas dar permiso al micrófono.";
            recordBtn.disabled = true;
        }
    };

    // ⏹️ Detener grabación
    stopBtn.onclick = () => {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            clearInterval(grabacionInterval);
            estado.textContent = "⏳ Transcribiendo...";
            mediaRecorder.stop();
        }
        recordBtn.disabled = false;
        stopBtn.disabled = true;
    };

    // 📝 Guardar comentario
    document.getElementById("formulario").onsubmit = async (e) => {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        formData.set("comentario", transcripcionTextarea.value);

        const payload = Object.fromEntries(formData.entries());

        if (navigator.onLine) {
            try {
                const res = await fetch("https://transcriptor-backend-jw83.onrender.com/guardar/", {
                    method: "POST",
                    body: formData
                });

                if (!res.ok) {
                    const errorText = await res.text();
                    throw new Error(`Error en el servidor al guardar: ${res.status} - ${errorText}`);
                }

                const data = await res.json();
                estado.textContent = `✅ ${data.mensaje}`;
            } catch (e) {
                console.error("Error al guardar online:", e);
                guardarOffline(payload);
            }
        } else {
            guardarOffline(payload);
        }

        form.reset();
        transcripcionTextarea.value = "";
        guardarBtn.disabled = true;
        player.src = "";
    };

    // 💾 Guardar localmente si está offline
    function guardarOffline(data) {
        const pendientes = JSON.parse(localStorage.getItem("pendientes") || "[]");
        pendientes.push(data);
        localStorage.setItem("pendientes", JSON.stringify(pendientes));
        estado.textContent = "💾 Guardado localmente (offline)";
    }

    // 🔁 Sincronizar cuando vuelve la conexión
    window.addEventListener("online", async () => {
        const pendientes = JSON.parse(localStorage.getItem("pendientes") || "[]");
        if (pendientes.length === 0) {
            estado.textContent = "✅ Conexión recuperada. No hay pendientes de sincronizar.";
            return;
        }

        estado.textContent = "🔄 Sincronizando pendientes...";
        let sincronizadosExitosos = 0;
        let erroresSincronizacion = 0;

        for (const dato of pendientes) {
            const formData = new FormData();
            for (let key in dato) {
                formData.append(key, dato[key]);
            }
            try {
                const res = await fetch("https://transcriptor-backend-jw83.onrender.com/guardar/", {
                    method: "POST",
                    body: formData
                });
                if (!res.ok) {
                    const errorText = await res.text();
                    throw new Error(`Error al sincronizar un pendiente: ${res.status} - ${errorText}`);
                }
                sincronizadosExitosos++;
            } catch (e) {
                console.error("Falló la sincronización de un pendiente:", e);
                erroresSincronizacion++;
            }
        }

        if (erroresSincronizacion === 0) {
            localStorage.removeItem("pendientes");
            estado.textContent = `✅ ${sincronizadosExitosos} pendientes sincronizados.`;
        } else {
            estado.textContent = `⚠️ Sincronizados ${sincronizadosExitosos}, fallaron ${erroresSincronizacion}.`;
        }
    });

    // 🚀 Iniciar
    cargarClientes();
});

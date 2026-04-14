let seleccionados = []

function toggleSeleccion(id){

if(seleccionados.includes(id)){

seleccionados = seleccionados.filter(i=>i!=id)

}else{

seleccionados.push(id)

}

}

function eliminar(id){

if(confirm("Eliminar registro?")){

fetch("/eliminar/"+id,{
method:"DELETE"
})
.then(()=>location.reload())

}

}

function ver(id){

window.open("/ver/"+id)

}

function descargar(id){

window.location="/descargar/"+id

}

function generarSeleccionados(){

fetch("/generar",{

method:"POST",
headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
ids:seleccionados
})

})
.then(res=>res.json())
.then(()=>location.reload())

}

function descargarZIP(){

window.location="/descargar_zip"

}
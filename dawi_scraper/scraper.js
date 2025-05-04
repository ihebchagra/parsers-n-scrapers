SERVER = {
	root: "https://dawi.tn",
	url_medicament: 'https://dawi.tn/json/medicament/',
	url_config: 'https://dawi.tn/json/config/'
}




console.save = function(data, filename){
    if(!data) {
        console.error('Console.save: No data')
        return;
    }
    if(!filename) filename = 'console.json'
    if(typeof data === "object"){
        data = JSON.stringify(data, undefined, 4)
    }
    var blob = new Blob([data], {type: 'text/json'}),
        e    = document.createEvent('MouseEvents'),
        a    = document.createElement('a')
    a.download = filename
    a.href = window.URL.createObjectURL(blob)
    a.dataset.downloadurl =  ['text/json', a.download, a.href].join(':')
    e.initMouseEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null)
    a.dispatchEvent(e)
}





var database=[]
function getPrices(){
	var n=0
	var number=data.length
	for(var i in data){
		n+=1
		var data_fields=Object.keys(data[i])
		var obj=data[i]
		mot=""
		if(data_fields.includes("Spécialité"))
			mot+=data[i]["Spécialité"] + " "
		if(data_fields.includes("Dosage"))
			mot+=data[i]["Dosage"].replace(/[a-z]/gi, '')  + " "
		if(data_fields.includes("Présentation"))
			mot+=data[i]["Présentation"].replace(/[^\d]/g,'') + " "
		mot = mot.trim()
		$.ajax({url:SERVER.url_medicament,async: false, data: {d: mot}}).done(function(results) {
			if (results.length < 1) {
				return;
			} else if (Object.keys(results).length !=1) {
				return;
			}
			var idmed = Object.keys(results)[0]
			$.ajax({url:SERVER.url_medicament,async: false, data: {id: idmed, term: localStorage['termid']}}).done(function(prix) {
				console.log(n,'/',number,mot, prix["prix_public"])
				obj["Prix"] = prix["prix_public"]+' DT'
			});
		});
		database.push(obj)
		//if (n>10)
			//break
	}
	const finaldb="data="+JSON.stringify(database)
	console.save(finaldb,"database.js")
}

ages = ["0", "2", "7", "17", "31", "41", "51", "61", "71", "81"]
sexes = ["MALE", "FEMALE"]
onsets = ["MINUTES", "HOURS", "DAYS", "WEEKS"]
pathologies = Object.keys(pathology_obj) 

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


for(var i=751;i<features.length;i++){
	console.log("FEATURE " + i + " : " + features[i])
	//if (i==751)
		//break

	//input to get data
	for(var u in sexes){
		for(var k in onsets){
			for(var j in ages){
				var inputs = {
					gender: sexes[u],
					age: ages[j],
					onset: onsets[k],
					features_present: [features[i]],
					features_absent: [],
					loaded_from_q: ''
				}

				//command to send a request, the promise stuff is for async
				$.ajax({url:'../pages/differential_diagnosis/data/load_results.php', data:inputs, async:true, dataType:'json'}).done(function(data){
					$('#middle_column').html(data.middle_column);
					// gets data from elements card by card
					if(document.getElementById("accordion")==null)
						return
					accordions=$("[id='accordion']") 
					for(var s=0; s<accordions.length; s++){
						accordion= accordions[s]
						cards= accordion.getElementsByClassName("card")
						for(var p=0; p<cards.length; p++){
							maladie=cards[p].getElementsByClassName("btn-link")[0].innerText
							//needs to check if already in list or not
							if( (!pathologies.includes(maladie)) && (maladie!="View dev log") ){
								console.log("NEW DETECTED : " + maladie)
								//new maladie routine
								//continue to get data because new to list
								pathology_obj[maladie] = {"arguments" : {}}
								pathologies.push(maladie)
								body=cards[p].getElementsByClassName("card-body")[0]
								//get arguments and put them in list
								symptoms=body.getElementsByTagName("li") 
								for(var n=0;n<symptoms.length;n++){
									text = symptoms[n].innerText
									re  = / \(\d+.*$/;
									symptomsText = text.replace(re.exec(text), "").split('  ')
									re = /\d+%/
									probability = re.exec(text)[0].replace("%","")
									for(var b=0;b<symptomsText.length;b++){
										symptom=symptomsText[b]
										if(features.includes(symptom)) {
											pathology_obj[maladie]["arguments"][symptom]=probability
										}
									}
								}
								//console.log(pathology_obj[maladie]["arguments"])
								//get bold text
								bolds = body.getElementsByTagName("b")
								for(var n=0;n<bolds.length;n++){
									//get incidence
									if(bolds[n].innerText.includes("Incidence")){
										pathology_obj[maladie]["incidence"]=bolds[n].nextSibling.data.split(" ")[0]
									//get sex ratio
									} else if (bolds[n].innerText.includes("Sex ratio")){
										text=bolds[n].nextSibling.data
										re=/\d+\.*\d*:\d+/
										ratio=re.exec(text)[0].replace(':1','')
										if (text.includes('females')) {
											pathology_obj[maladie]["sex"]='F' + ratio
										} else if(text.includes('males')) {
											pathology_obj[maladie]["sex"]='M' + ratio
										} else if(ratio == '1') {
											pathology_obj[maladie]["sex"]= '1'
										}
									}
								}
								//handle exception where no sex ratio if only one sex
								// we won't use this for speed purpose
								//if (pathology_obj[maladie]["sex"]==undefined)
									//pathology_obj[maladie]["sex"]=sexes[u][0]
								//console.log(pathology_obj[maladie]["incidence"])
								//console.log(pathology_obj[maladie]["sex"])
								//get tables
								tables = body.getElementsByTagName("tbody")
								//get incidence by age
								age_table=tables[0]
								var age_incidences={}
								for(var n=1;n<11;n++){
									age_incidences[n]=0
									if ( $("[id='square-age_" + n + "_1']",age_table)[0].classList.contains("blue") ){
										for(var b=1;b<21;b++){
											if ( $("[id='square-age_" + n + "_" + b +"']",age_table)[0].classList.contains("blue") ){
												age_incidences[n]=b
											} else {
												break
											}
										}
									}
								}
								pathology_obj[maladie]["age"]=age_incidences
								//console.log(age_incidences)
								//get incidence by onset
								onset_table=tables[1]
								var onset_incidences={}
								for(var n=1;n<5;n++){
									onset_incidences[n]=0
									if ( $("[id='square-onset_" + n + "_1']",onset_table)[0].classList.contains("red") ){
										for(var b=1;b<21;b++){
											if ( $("[id='square-onset_" + n + "_" + b +"']",onset_table)[0].classList.contains("red") ){
												onset_incidences[n]=b
											} else {
												break
											}
										}
									}
								}
								pathology_obj[maladie]["onset"]=onset_incidences
								//console.log(onset_incidences)
							} else if (maladie!="View dev log") {
								//check if new arguments and update them
								body=cards[p].getElementsByClassName("card-body")[0]
								//get arguments and put them in list
								symptoms=body.getElementsByTagName("li") 
								for(var n=0;n<symptoms.length;n++){
									text = symptoms[n].innerText
									re  = / \(\d+.*$/;
									symptomsText = text.replace(re.exec(text), "").split('  ')
									re = /\d+%/
									probability = re.exec(text)[0].replace("%","")
									for(var b=0;b<symptomsText.length;b++){
										symptom=symptomsText[b]
										if(pathology_obj[maladie]["arguments"][symptom]!=undefined){
											continue
										}
										if(features.includes(symptom)) {
											console.log("UPDATED : " + symptom + " @ " + maladie)
											pathology_obj[maladie]["arguments"][symptom]=probability
										}
									}
								}
								continue
							}
						}
					}
				})
			};
		}
	}
}



//console.save(pathology_obj,"database.json")

function httpGET(url, callback) {
    const http = new XMLHttpRequest();
    http.open("GET", url, true);
    http.onreadystatechange=(e)=>{
        if (http.readyState == 4 && http.status == 200)
            callback(http.responseText);
    }
    http.send();
}

function httpPOST(url, callback, json) {
    const http = new XMLHttpRequest();
    http.open("POST", url, true);
    http.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    http.onreadystatechange=(e)=>{
        if (http.readyState == 4)
            callback(http.responseText, http.status);
    }
    http.send(JSON.stringify(json));
}

function postValues() {
    var inputDateVar = document.getElementById("date").value;
    var inputStock = document.getElementById("stock").value;
    var inputQuantity = document.getElementById("quantity").value;
    var inputValue = document.getElementById("value").value;
    var inputTaxes = document.getElementById("taxes").value;
    var inputBroker = document.getElementById("broker").value;
    var inputClass = document.getElementById("classes").value;
    var inputComments = document.getElementById("comments").value;
    if (inputDateVar=="" || inputStock=="" || inputValue=="") {
        alert("You must fill all required fields:\n\tDate\n\Stock\n\tQuantity\n\tValue");
        return;
    }
    var json = {};
    json["date"] = inputDateVar;
    json["stock"] = inputStock;
    json["quantity"] = Number(inputQuantity);
    json["value"] = Number(inputValue);
    json["taxes"] = Number(inputTaxes);
    json["broker"] = "Clear";
    json["stock_class"] = "";
    json["comments"] = "";
    $.ajax({
        url: 'http://127.0.0.1:8080/stock/',
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        data: $.toJSON(json),
        dataType: 'text',
        success: function(result) {
            alert(result.Result);
        }
    });
    //httpPOST("http://127.0.0.1:8080/stock", callbackPOST, json);
}

function callbackPOST (response, status) {
    if (status == 200) {
        document.getElementById("date").value = "";
        document.getElementById("stock").value = "";
        document.getElementById("quantity").value = "";
        document.getElementById("value").value = "";
        document.getElementById("taxes").value = "";
        document.getElementById("broker").value = "Broker";
        document.getElementById("classes").value = "Classes";
        document.getElementById("comments").value = "Comments...";
        //httpGET("http://127.0.0.1:8080/stock", insertLast);
    } else if (status == 409) {
        setTimeout(function(){
            alert(response);
        },2000);
    } else {
        setTimeout(function(){
            alert("Shenanigans!!");
        },2000);
    }
}
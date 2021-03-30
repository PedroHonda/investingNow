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
    json["ticker"] = inputStock;
    json["quantity"] = Number(inputQuantity);
    json["value"] = Number(inputValue);
    json["taxes"] = Number(inputTaxes);
    json["broker"] = inputBroker;
    if (inputClass == "Classes")
        json["stock_class"] = "";
    else
        json["stock_class"] = inputClass;
    json["comments"] = inputComments;
    $.ajax({
        url: 'http://127.0.0.1:8000/stock/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(json),
        dataType: 'json',
        success: function(result) {
            location.replace("http://127.0.0.1:8000/view/stock/" + inputStock);
        }
    });
}
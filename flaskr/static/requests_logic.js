// Search as you type - autocompletion
$('#userInput').keyup(function(e) {
    console.log("Pressed key");

    userInput = $("#userInput").val();
    $.ajax({
        type: "GET",
        url: "/autocomplete",
        data: {
            'user_input' : userInput
        },                                
        success: function(result){
            responseStr = JSON.stringify(result[0]);
            //console.log(result[0]);

            // Create suggestion drop down
            if(result[0] != "No suggestion found"){
              $('#suggestion').css({"display" : "block"});                      
              $('#suggestionSpan').text(result[0]);
              $('#suggestionSpan').css({"color" : "black", "cursor" : "pointer"});
            } else {
              $('#suggestion').css({"display" : "none"});
            }                    
        }
    });
});

// Append suggestion to the input field
$("#suggestionSpan").click(function(){
    console.log("Using suggestion");
    $("#userInput").val($("#userInput").val() + " " + $('#suggestionSpan').text());
});


// Process order request
$("#inputBtn").click(function(){
    userInput = $("#userInput").val();
    $.ajax({
        type: "POST",
        url: "/prompt",
        data: {
            'user_input' : userInput
        },                                
        success: function(result){
            responseStr = JSON.stringify(result[0]);            
            topics = result[3];
            topicExtractionType = result[4];
            topicArr = [];            

            if(topicExtractionType == "NN"){
                topics.forEach(element =>{
                    console.log("NN topic word: ", element[0])
                    topicArr.push(element[0]);
                });
            } else {
                topics.forEach(element => {
                    console.log("LDA topic word", element)
                    topicArr.push(element);
                });
            }

            console.log('Extracted topic words: ', topicArr);

            resultResponse = responseStr.slice(1,-1);
         
            $("#responseText").text(resultResponse);                  
            resultPercentege = JSON.stringify(result[1]) + " %";
          
            $("#accText").text(resultPercentege);    
            resultTotalPrice = JSON.stringify(result[2]);

            // Precision
            resultTotalPrice = (Number(resultTotalPrice).toFixed(2)).toString();                                     
            $("#totalPrice").text(resultTotalPrice + " $");
        }, 
        error: function (error) {
            $("p").text(error);
        }   
    });
});

// Generate receipt request
$("#generateReceiptButton").click(function(){
    console.log("Triggering receipt generation");
    userInput = $("#userInput").val();
    $.ajax({
        type: "GET",
        url: "/receipt",
        data: {
            'user_input' : ""
        },
        success: function(result){
            responseStr = JSON.stringify(result[0]);
            receiptName = result[0];
            console.log(receiptName);                                                         
        }, 
        error: function (error) {
            $("p").text(error);
        }   
    });
});
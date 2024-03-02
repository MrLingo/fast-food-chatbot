var inputFieldHeight = 3;


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



function displayProducts(productsOBJ){                  
    for(let i = 0; i < productsOBJ.length; i++){
        // Outer wrapper
        const productElement = document.createElement('div');
        productElement.setAttribute("class", "product");
        $("#productsList").append(productElement);
        
        // Add product image
        const productElementInner = document.createElement('img');
        productElementInner.setAttribute("class", "productImage");
        productElementInner.setAttribute("src", productsOBJ[i].src_name);
        productElement.appendChild(productElementInner);
       
        // Add product description and price
        const productDescription = document.createElement('div');
        productDescription.setAttribute("class", "productDescription");
        productDescription.innerText = productsOBJ[i].name + "\n" +  
                                       "Price: " + productsOBJ[i].price + "\n" +  
                                       "Ingredients:\n" + productsOBJ[i].ingredients;
        productElement.appendChild(productDescription);
    }                         
}

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
            //recommendedTopics = result[5];        
            productsArr = result[5];   

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

            function displayRecommendedTopics(recommendedTopics){
                // Reset
                $("#recommendedTopics").innerText = "";

                for(let i = 0; i < recommendedTopics.length; i++){
                  const topic = document.createElement("div");
                  topic.setAttribute("class", "recommendedTopic");

                  console.log("recommended topic  ", recommendedTopics[i]);

                  topic.innerText = recommendedTopics[i];
                  $("#recommendedTopics").append(topic);
                }                  
              }

            // Reset product area
            if(document.querySelector('.product')){
                document.querySelectorAll('.product').forEach(e => e.remove());
            }
            
            console.log(productsArr);
            displayProducts(productsArr);
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
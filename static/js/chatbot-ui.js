/*
Makes backend API call to HumanyTek chatbot and display output to chatbot frontend
*/
host = 'https://ia.humanytek.com/api/chatbot'

widget_id = ""
botLogoPath = ""
botName = ""
welcomeMessage = "Hi, how can I assit you today?"
theme = "blue"
function init() {

    //--------------------------- Chatbot Frontend -------------------------------
    const chatContainer = document.getElementById("chat-container");

    template = ` <button class='chat-btn'><img src = "/static/icons/comment.png" class = "icon" ></button>
    
    <div class='chat-popup'>
    
		<div class='chat-header'>
			<div class='chatbot-img'>
				<img src='${botLogoPath}' alt='Chat Bot image' class='bot-img'> 
			</div>
			<h3 class='bot-title'>'${botName}'</h3>
			<button class = "expand-chat-window" ><img src="/static/icons/open_fullscreen.png" class="icon" ></button>
		</div>

		<div class='chat-area'>
            <div class='bot-msg'>
                <img class='bot-img' src ='${botLogoPath}' />
				<span class='msg'>'${welcomeMessage}'</span>
			</div>

            <!-- <div class='bot-msg'>
                <img class='bot-img' src ='${botLogoPath}' />
                <div class='response-btns'>
                    <button class='btn-primary' onclick= 'userResponseBtn(this)' value='/sign_in'>sample btn</button>            
                </div>
			</div> -->

			<!-- <div class='bot-msg'>
				<img class='msg-image' src = "https://i.imgur.com/nGF1K8f.jpg" />
			</div> -->

			<!-- <div class='user-msg'>
				<span class='msg'>Hi, How can i help you?</span>
			</div> -->
			

		</div>


		<div class='chat-input-area'>
			<input type='text' autofocus class='chat-input' onkeypress='return givenUserInput(event)' placeholder='Type a message ...' autocomplete='off'>
			<button class='chat-submit'><i class='material-icons'>send</i></button>
		</div>

	</div>`


    chatContainer.innerHTML = template;

    //--------------------------- Important Variables----------------------------
    var inactiveMessage = "Server is down, Please contact the developer to activate it"


    chatPopup = document.querySelector(".chat-popup")
    chatBtn = document.querySelector(".chat-btn")
    chatSubmit = document.querySelector(".chat-submit")
    chatHeader = document.querySelector(".chat-header")
    chatArea = document.querySelector(".chat-area")
    chatInput = document.querySelector(".chat-input")
    expandWindow = document.querySelector(".expand-chat-window")
    root = document.documentElement;
    chatPopup.style.display = "none"

    //------------------------ ChatBot Toggler -------------------------

    chatBtn.addEventListener("click", () => {

        mobileDevice = !detectMob()
        if (chatPopup.style.display == "none" && mobileDevice) {
            chatPopup.style.display = "flex"
            chatInput.focus();
            chatBtn.innerHTML = `<img src = "/static/icons/close.png" class = "icon" >`
        } else if (mobileDevice) {
            chatPopup.style.display = "none"
            chatBtn.innerHTML = `<img src = "/static/icons/comment.png" class = "icon" >`
        } else {
            mobileView()
        }
    })

    chatSubmit.addEventListener("click", () => {
        let userResponse = chatInput.value.trim();
        if (userResponse !== "") {
            setUserResponse();
            send(userResponse)
        }
    })

    expandWindow.addEventListener("click", (e) => {
        // console.log(expandWindow.innerHTML)
        if (expandWindow.innerHTML == '<img src="/static/icons/open_fullscreen.png" class="icon">') {
            expandWindow.innerHTML = `<img src = "/static/icons/close_fullscreen.png" class = 'icon'>`
            root.style.setProperty('--chat-window-height', 80 + "%");
            root.style.setProperty('--chat-window-total-width', 85 + "%");
        } else if (expandWindow.innerHTML == '<img src="/static/icons/close.png" class="icon">') {
            chatPopup.style.display = "none"
            chatBtn.style.display = "block"
        } else {
            expandWindow.innerHTML = `<img src = "/static/icons/open_fullscreen.png" class = "icon" >`
            root.style.setProperty('--chat-window-height', 500 + "px");
            root.style.setProperty('--chat-window-total-width', 380 + "px");
        }

    })
}

// end of init function



var passwordInput = false;

function userResponseBtn(e) {
    send(e.value);
}

// to submit user input when he presses enter
function givenUserInput(e) {
    if (e.keyCode == 13) {
        let userResponse = chatInput.value.trim();
        if (userResponse !== "") {
            setUserResponse()
            send(userResponse)
        }
    }
}

// to display user message on UI
function setUserResponse() {
    let userInput = chatInput.value;
    if (passwordInput) {
        userInput = "******"
    }
    if (userInput) {
        let temp = `<div class="user-msg"><span class = "msg">${userInput}</span></div>`
        chatArea.innerHTML += temp;
        chatInput.value = ""
    } else {
        chatInput.disabled = false;
    }
    scrollToBottomOfResults();
}



function scrollToBottomOfResults() {
    chatArea.scrollTop = chatArea.scrollHeight;
}

/***************************************************************
Frontend Part Completed
****************************************************************/

function send(message) {
    chatInput.type = "text"
    passwordInput = false;
    chatInput.focus();
    console.log("User Message:", message)
    $.ajax({
        url: `${host}/call?message=${message}&widget_id=${widget_id}`,
        headers: {
            'Authorization': `Bearer A8qKxaj3vHrF2jATS5q7ooxMvkId91FuZaf1l6UPQqII4IECv2KRkjSE4b8DZBwO`
        },
        type: 'GET',
        contentType: 'application/json',
        success: function(data, textStatus) {
            if (data.message != null) {
                setBotResponse(data.message);
            }
            console.log("HumanyTek Response: ", data.message, "\n Status:", textStatus)
        },
        error: function(errorMessage) {
            setBotResponse("");
            console.log('Error' + errorMessage);

        }
    });
    chatInput.focus();
}

//------------------------------------ Set bot response -------------------------------------
function setBotResponse(val) {
    setTimeout(function() {
        if (val.length < 1) {
            //if there is no response from HumanyTek
            // msg = 'I couldn\'t get that. Let\' try something else!';
            msg = inactiveMessage;

            var BotResponse = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><span class='msg'> ${msg} </span></div>`;
            $(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);
            scrollToBottomOfResults();
            chatInput.focus();

        } else {
            //if we get response from HumanyTek
            for (i = 0; i < val.length; i++) {
                //check if there is text message
                if (val[i].hasOwnProperty("text")) {
                    const botMsg = val[i].text;
                    if (botMsg.includes("password")) {
                        chatInput.type = "password";
                        passwordInput = true;
                    }
                    var BotResponse = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><span class='msg'>${val[i].text}</span></div>`;
                    $(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);
                }

                //check if there is image
                if (val[i].hasOwnProperty("image")) {
                    var BotResponse = "<div class='bot-msg'>" + "<img class='bot-img' src ='${botLogoPath}' />"
                    '<img class="msg-image" src="' + val[i].image + '">' +
                        '</div>'
                    $(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);
                }

                //check if there are buttons
                if (val[i].hasOwnProperty("buttons")) {
                    var BotResponse = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><div class='response-btns'>`

                    buttonsArray = val[i].buttons;
                    buttonsArray.forEach(btn => {
                        BotResponse += `<button class='btn-primary' onclick= 'userResponseBtn(this)' value='${btn.payload}'>${btn.title}</button>`
                    })

                    BotResponse += "</div></div>"

                    $(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);
                    chatInput.disabled = true;
                }

            }
            scrollToBottomOfResults();
            chatInput.disabled = false;
            chatInput.focus();
        }

    }, 500);
}




function mobileView() {
    $('.chat-popup').width($(window).width());

    if (chatPopup.style.display == "none") {
        chatPopup.style.display = "flex"
            // chatInput.focus();
        chatBtn.style.display = "none"
        chatPopup.style.bottom = "0"
        chatPopup.style.right = "0"
            // chatPopup.style.transition = "none"
        expandWindow.innerHTML = `<img src = "/static/icons/close.png" class = "icon" >`
    }
}

function detectMob() {
    return ((window.innerHeight <= 800) && (window.innerWidth <= 600));
}

function chatbotTheme(theme) {
    const gradientHeader = document.querySelector(".chat-header");
    const orange = {
        color: "#FBAB7E",
        background: "linear-gradient(19deg, #FBAB7E 0%, #F7CE68 100%)"
    }

    const purple = {
        color: "#B721FF",
        background: "linear-gradient(19deg, #21D4FD 0%, #B721FF 100%)"
    }



    if (theme === "orange") {
        root.style.setProperty('--chat-window-color-theme', orange.color);
        gradientHeader.style.backgroundImage = orange.background;
        chatSubmit.style.backgroundColor = orange.color;
    } else if (theme === "purple") {
        root.style.setProperty('--chat-window-color-theme', purple.color);
        gradientHeader.style.backgroundImage = purple.background;
        chatSubmit.style.backgroundColor = purple.color;
    }
}

function import_chatbot_setting(){
    $.ajax({
        url: `${host}/details?widget_id=${widget_id}`,
        type: 'GET',
        headers: {
            'Authorization': `Bearer A8qKxaj3vHrF2jATS5q7ooxMvkId91FuZaf1l6UPQqII4IECv2KRkjSE4b8DZBwO`
          },
        contentType: 'application/json',
        success: function(data, textStatus) {
            if (data.logo != null) {
                botLogoPath = data.logo
            }
            if (data.name != null) {
                botName = data.name
            }
            if (data.welcomeMessage != null) {
                welcomeMessage = data.welcomeMessage
            }
            if (data.theme != null) {
                theme = data.theme
            }
            init()
            chatbotTheme(theme)
        },
        error: function(errorMessage) {
            setBotResponse("");
            console.log('Error' + errorMessage);

        }
    });
}

function createChatBot(id) {
//--------------------------- Important Variables----------------------------
    widget_id = id;
    import_chatbot_setting();
}
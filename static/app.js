class Chatbox {
  constructor() {
    this.args = {
      openButton: document.querySelector(".chatbox__button"),
      chatBox: document.querySelector(".chatbox__support"),
      sendButton: document.querySelector(".send__button"),
    };

    this.state = false;
    this.messages = [];
    this.username = "";
  }

  getName(chatbox) {
    const name = prompt("Please enter your name");
    if (name) {
      this.userName = name;
      const welcomeMsg = `Hi ${this.userName}! My name is Bot. How can I help you?`;
      let msg1 = { name: "Bot", message: welcomeMsg };
      this.messages.push(msg1);
      this.updateChatText(chatbox);
    } else {
      this.getName(chatbox);
    }
  }


  display() {
    const { openButton, chatBox, sendButton } = this.args;

    openButton.addEventListener("click", () => {
      if (!this.userName) {
        this.getName(chatBox);
      }
      this.toggleState(chatBox);
    });

    sendButton.addEventListener("click", () => this.onSendButton(chatBox));

    const node = chatBox.querySelector("input");
    node.addEventListener("keyup", ({ key }) => {
      if (key === "Enter") {
        this.onSendButton(chatBox);
      }
    });
  }

  toggleState(chatbox) {
    this.state = !this.state;

    // show or hides the box
    if (this.state) {
      chatbox.classList.add("chatbox--active");
    } else {
      chatbox.classList.remove("chatbox--active");
    }
  }



  sendRating(username, rating) {
    fetch('/rating', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({name: username, rating: rating})
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log(data);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }
  

  onSendButton(chatbox) {
    var textField = chatbox.querySelector("input");
    let text1 = textField.value;
    if (text1 === "") {
      return;
    }

    let msg1 = { name: "User", message: text1 };
    this.messages.push(msg1);

    fetch("/predict", {
      method: "POST",
      body: JSON.stringify({ message: text1 }),
      mode: "cors",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((r) => r.json())
      .then((r) => {
        let msg2 = { name: "Bot", message: r.answer };
        this.messages.push(msg2);
        this.updateChatText(chatbox);
        textField.value = "";
        if (msg2.message.includes("Thank you for chatting with me!")) {
          let responses = msg2.message.split(' & ');
  for (let i = 0; i < responses.length; i++) {
    let response = responses[i].trim();
    if (response.length > 0) {
      this.messages.push({ name: "Bot", message: response });
      
    }
  }

  this.updateChatText(chatbox);
          
          this.onEndChat(chatbox);
        }
        else{
          alert("inside else");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        this.updateChatText(chatbox);
        textField.value = "";
      });
  }

  onEndChat(chatbox) {
    const rating = prompt("Please rate your experience out of 5");
    // store the rating somewhere
    let endMsg = `Thank you for chatting with me, ${this.userName}!`;
    let msg3 = { name: "Bot", message: endMsg };
    this.messages.push(msg3);
    this.updateChatText(chatbox);
    this.sendRating(this.userName, rating);
  }

  updateChatText(chatbox) {
    var html = "";
    this.messages
      .slice()
      .reverse()
      .forEach(function (item, index) {
        if (item.name === "Bot") {
          html +=
            '<div class="messages__item messages__item--visitor">' +
            `<p>${item.message}</p>` +
            "</div>";
        } else {
          html +=
            '<div class="messages__item messages__item--operator">' +
            `<p>${item.message}</p>` +
            "</div>";
        }
      });

    const chatmessage = chatbox.querySelector(".chatbox__messages");
    chatmessage.innerHTML = html;
  }
}

const chatbox = new Chatbox();
chatbox.display();

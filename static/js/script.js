//first page to mid page
function redirectToDashboard() {
    // Redirect to the Flask route
    // Delay the page change to allow the transition to complete
    setTimeout(() => {
        window.location.href = "/dashboard"; // Replace with your new page URL
    }, 1000); // Delay time should match the transition duration in CSS
}

function showSection() {
    window.location.href = "/dashboard";
}


function selectSection(sectionId) {
    // Remove 'active' class from all nav items
    document.querySelectorAll('.nav-link').forEach(item => {
        item.classList.remove('active');
    });

    // Add 'active' class to the selected nav item
    document.getElementById(sectionId).classList.add('active');

    // Display username input form in the content area
    document.getElementById('content-area').innerHTML = `
        <div id="username-form">
            <h1>Welcome to <span>${sectionId}!</span></h1>
            <p>To get started, please enter your username below:</p>
            <input type="text" id="username-input" placeholder="Username">
            <button onclick="submitUsername('${sectionId}')">Submit</button>
        </div>
    `;
}

function submitUsername(sectionId) {
    const username = document.getElementById('username-input').value;

    if (username) {
        fetch('/get_content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `section_id=${sectionId}&username=${username}`
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById('content-area').innerHTML = data.content;
                attachEventListeners();
            });
    } else {
        alert("Please enter a username.");
    }
}

function attachEventListeners() {
    document.getElementById('show-box-btn').addEventListener('click', function () {
        document.getElementById('scroll-box').style.display = 'block';
    });

    // Reattach event listeners to any other dynamically loaded elements
    const sidemenu = document.querySelector("aside");
    const menubtn = document.querySelector("#menu_bar");
    const closebtn = document.querySelector("#close_btn");

    menubtn.addEventListener('click', () => {
        sidemenu.style.display = 'block';
    });

    closebtn.addEventListener('click', () => {
        sidemenu.style.display = 'none';
    });

    const themetoggler = document.querySelector(".theme-toggler");
    themetoggler.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme-variables');
        themetoggler.querySelector('span:nth-child(1)').classList.toggle('active');
        themetoggler.querySelector('span:nth-child(2)').classList.toggle('active');
    });

    //date adding
    const dateInput = document.getElementById('date-input');

    const today = new Date();
    const day = String(today.getDate()).padStart(2, '0');
    const month = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    const year = today.getFullYear();

    const formattedDate = `${year}-${month}-${day}`;

    dateInput.value = formattedDate;
    $(document).ready(function () {
        $('#show-box-btn').click(function () {
            $.ajax({
                url: '/get-suggestions',
                method: 'POST',
                success: function (response) {
                    if (response.suggestions) {
                        let formattedResponse = response.suggestions
                            .split('\n\n')
                            .map(paragraph => `<li><p>${paragraph}</p></li>`)
                            .join('');

                        $('#scroll-box').html(formattedResponse);
                    } else {
                        $('#scroll-box').html('<p>No suggestions found.</p>');
                    }
                },
                error: function (err) {
                    $('#scroll-box').html('<p>Error retrieving suggestions. Please try again later.</p>');
                }
            });
        });
    });


    document.getElementById('add-friend-btn').addEventListener('click', function () {
        document.getElementById('friend-input-container').style.display = 'block';
    });


    document.getElementById('submit-friend-btn').addEventListener('click', function () {
        const username = document.getElementById('friend-username').value;
        if (username) {
            // Hide input and button
            document.getElementById('friend-input-container').style.display = 'none';

            // Display the table if it's hidden
            document.getElementById('friends-table').style.display = 'table';

            fetch('/add-friend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username: username })
            })
                .then(response => response.json())
                .then(data => {
                    // Update the table with the correct username and problems solved
                    const problemsSolved = data.problems_solved;

                    // Append the friend to the table
                    const friendItem = `
                <tr>
                    <td>${document.getElementById('friends-list-container').children.length + 1}</td>
                    <td>${username}</td>
                    <td>${problemsSolved}</td>
                </tr>`;
                    document.getElementById('friends-list-container').insertAdjacentHTML('beforeend', friendItem);
                })
                .catch(error => console.error('Error:', error));
        }

    });
}

attachEventListeners();



// static/scripts.js





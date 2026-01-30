document.addEventListener("DOMContentLoaded", () => {
    team_list();
    unknow_user_list();
});
// repeat
setInterval(team_list, 10000);
setInterval(unknow_user_list, 10000);

function team_list() {
    const team = document.getElementById('team').textContent;
    fetch(`/api/team/${team}`)
        .then(response => response.json())
        .then(data => { 
            // 獲取標籤
            const label = document.getElementById('teammate_list_label');
            const adminsList = document.getElementById('admins_list');
            const playersList = document.getElementById('players_list');
            const setStation = document.getElementById('set_station');
            const set_station_label = document.getElementById('set_station_label');

            // 顯示設定初始站點選項
            const startStationDefined = data.start_location_defined;
            if (!startStationDefined) {
                setStation.style.display = 'block';
                set_station_label.style.display = 'block';
            } else {
                setStation.style.display = 'none';
                set_station_label.style.display = 'none';
            }

            // 清空先前的內容
            adminsList.innerHTML = '';
            playersList.innerHTML = '';

            // 顯示 admins
            if (data.admins && data.admins.length > 0) {
                adminsList.innerHTML = '<h3>Admins</h3>';
                data.admins.forEach(admin => {
                    const listItem = document.createElement('li');
                    listItem.textContent = admin;
                    adminsList.appendChild(listItem);
                });
            } else {
                adminsList.innerHTML = '<p>No admins found.</p>';
            }

            // 顯示 players
            if (data.players && data.players.length > 0) {
                playersList.innerHTML = '<h3>Players</h3>';
                data.players.forEach(player => {
                    const listItem = document.createElement('li');
                    listItem.textContent = player;
                    playersList.appendChild(listItem);
                });
            } else {
                playersList.innerHTML = '<p>No players found.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching team data:', error);
            const label = document.getElementById('teammate_list_label');
            label.textContent = 'Error loading team data.';
        });
}


function set_station() {
    const team = document.getElementById('team').textContent;
    const station = document.getElementById('station_name').value;
    fetch(`/api/set_station/${team}/${station.replaceAll('/', '_')}`)
        .then(response => response.text())
        .then(response => { alert(response); });
}

function join_team() {
    const team = document.getElementById('team').textContent;
    const player_name = document.getElementById('join_team_user-name').value;
    fetch(`/api/join_team/${team}/${player_name}`)
        .then(response => response.text())
        .then(response => { alert(response); });
}

function leave_team() {
    const player_name = document.getElementById("leave_team_user-name").value;
    fetch(`/api/leave_team/${player_name}`)
        .then(response => response.text())
        .then(response => { alert(response); });
}

document.addEventListener('DOMContentLoaded', (event) => {
    const rangeSlider = document.getElementById('rangeSlider');
    const rangeInput = document.getElementById('rangeInput');
    const rangeValue = document.getElementById('rangeValue');

    rangeSlider.addEventListener('input', function() {
        const value = this.value;
        rangeValue.textContent = value;
        rangeInput.value = value;
    });

    rangeInput.addEventListener('input', function() {
        const value = this.value;
        rangeValue.textContent = value;
        rangeSlider.value = value;
    });
});

function add_point() {
    const team = document.getElementById('team').textContent;
    const points = document.getElementById('rangeValue').textContent;
    fetch(`/api/add_point/${team}/${points}`)
        .then(response => response.text())
        .then(response => { alert(response); });
}

function unknow_user_list() {
    fetch('/api/users')
    .then(response => response.json())
    .then(data => {
        const userList = document.getElementById('unknow_user_list');
        userList.innerHTML = ''; 

        data.forEach(user => {
            const listItem = document.createElement('li');
            listItem.textContent = user;
            
            listItem.addEventListener('click', () => {
                navigator.clipboard.writeText(user)
                    .then(() => alert(`Copied: ${user}`))
                    .catch(err => console.error('Failed to copy text:', err));
            });

            userList.appendChild(listItem);
        });
    })
    .catch(error => {
        console.error('Error fetching user data:', error);
    });
}

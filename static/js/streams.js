const APP_ID = JSON.parse(document.getElementById('app_id').textContent);
const TOKEN = JSON.parse(document.getElementById('token').textContent);
const CHANNEL = JSON.parse(document.getElementById('channel').textContent);

let  UID = Number(JSON.parse(document.getElementById('uid').textContent));
let  USER_ID = Number(JSON.parse(document.getElementById('user_id').textContent));
let  MEETING_ID = Number(JSON.parse(document.getElementById('room_id').textContent));

const client = AgoraRTC.createClient({mode:'rtc', codec:'vp8'});

let localTracks = [];
let remoteUsers = {};


let joinAndDisplayLocalStream = async () => {
    client.on('user-published', handleUserJoined);
    client.on('user-left', handleUserLeft);

    let member = await createMember(USER_ID, MEETING_ID);

    let uid = await client.join(APP_ID, CHANNEL, member.token, member.uid);

    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks();

    let player = createMemberHTML(uid, member.user.username, true);
    document.getElementById('video-streams').insertAdjacentHTML('beforeend', player);
    localTracks[1].play(`user-${uid}`);
    await client.publish([localTracks[0], localTracks[1]]);
}

let handleUserJoined = async (user, mediaType) => {
    remoteUsers[user.uid] = user
    await client.subscribe(user, mediaType)

    let member = await getMember(user.uid, CHANNEL)

    if (mediaType === 'video'){
        let player = document.getElementById(`user-container-${user.uid}`)
        if (player != null) player.remove();

        player = createMemberHTML(user.uid, member.user.username);
        document.getElementById('video-streams').insertAdjacentHTML('beforeend', player)
        user.videoTrack.play(`user-${user.uid}`)
    }

    if (mediaType === 'audio'){
        user.audioTrack.play()
    }
}

let handleUserLeft = async (user) => {
    delete remoteUsers[user.uid]
    document.getElementById(`user-container-${user.uid}`).remove()
}

let toggleCamera = async (e) => {
    if(localTracks[1].muted){
        await localTracks[1].setMuted(false)
        e.target.style.backgroundColor = '#fff'
    }else{
        await localTracks[1].setMuted(true)
        e.target.style.backgroundColor = 'rgb(255, 80, 80, 1)'
    }
}

let toggleMic = async (e) => {
    if(localTracks[0].muted){
        await localTracks[0].setMuted(false)
        e.target.style.backgroundColor = '#fff'
    }else{
        await localTracks[0].setMuted(true)
        e.target.style.backgroundColor = 'rgb(255, 80, 80, 1)'
    }
}

function createMemberHTML(uid, name, is_current_user=false){
    if(is_current_user)
        return '<div  class="video-container-me" id="user-container-' + uid + '">' +
                '<div class="video-player" id="user-' + uid + '"></div>' +
                '<div class="username-wrapper">' +
                     '<span class="user-name">' + name + '</span>' +
                 '</div>' +
           '</div>';
    return '<div  class="video-container" id="user-container-' + uid + '">' +
                '<div class="video-player" id="user-' + uid + '"></div>' +
                '<div class="username-wrapper">' +
                     '<span class="user-name">' + name + '</span>' +
                 '</div>' +
           '</div>';
}

let leaveAndRemoveLocalStream = async () => {
    for (let i=0; localTracks.length > i; i++){
        localTracks[i].stop()
        localTracks[i].close()
    }

    await client.leave()
    //This is somewhat of an issue because if user leaves without actual pressing leave button, it will not trigger
    window.open('/', '_self')
}

let createMember = async (user_id, meeting_id) => {
    const formData = new FormData();
    formData.append('user', user_id);
    formData.append('meeting', meeting_id);
    let response = await fetch(window.location.origin+"/meeting/member/create/", {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    return data.data;
}

let getMember = async (uid, channel) => {
    let response = await fetch(window.location.origin+`/meeting/member/get/${uid}/${channel}/`);
    const data = await response.json();
    return data.data;
}


joinAndDisplayLocalStream();

// Event Listener
document.getElementById('leave-btn').addEventListener('click', leaveAndRemoveLocalStream)
document.getElementById('camera-btn').addEventListener('click', toggleCamera)
document.getElementById('mic-btn').addEventListener('click', toggleMic)

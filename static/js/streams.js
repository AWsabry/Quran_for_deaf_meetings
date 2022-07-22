const APP_ID = JSON.parse(document.getElementById('app_id').textContent);
const TOKEN = JSON.parse(document.getElementById('token').textContent);
const CHANNEL = JSON.parse(document.getElementById('channel').textContent);
let NAME = JSON.parse(document.getElementById('name').textContent);
let  UID = Number(JSON.parse(document.getElementById('uid').textContent));

const client = AgoraRTC.createClient({mode:'rtc', codec:'vp8'});

let localTracks = [];
let remoteUsers = {};

let joinAndDisplayLocalStream = async () => {
    client.on('user-published', handleUserJoined);
    client.on('user-left', handleUserLeft);

    UID = await client.join(APP_ID, CHANNEL, TOKEN, UID);
    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks();

    let player = createMemberHTML(UID, NAME);
    document.getElementById('video-streams').insertAdjacentHTML('beforeend', player);
    localTracks[1].play(`user-${UID}`);
    await client.publish([localTracks[0], localTracks[1]]);
}

let handleUserJoined = async (user, mediaType) => {
    remoteUsers[user.uid] = user
    await client.subscribe(user, mediaType)

    if (mediaType === 'video'){
        let player = document.getElementById(`user-container-${user.uid}`)
        if (player != null) player.remove()

        player = createMemberHTML(user.uid);
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

function createMemberHTML(uid, name){
    if (name==null) name = uid;
    if(UID === uid) return '<div  class="video-container-me" id="user-container-' + uid + '">' +
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


joinAndDisplayLocalStream();

// Event Listener
document.getElementById('leave-btn').addEventListener('click', leaveAndRemoveLocalStream)
document.getElementById('camera-btn').addEventListener('click', toggleCamera)
document.getElementById('mic-btn').addEventListener('click', toggleMic)

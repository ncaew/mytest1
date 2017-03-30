
function vlc_init()
{

	console.log("!!!vlc vlc_init");
    if( navigator.appName.indexOf("Microsoft Internet") == -1 )
    {
        onVLCPluginReady()
    }
    else if( document.readyState == 'complete' )
    {
        onVLCPluginReady();
    }
    else
    {
        /* Explorer loads plugins asynchronously */
        document.onreadystatechange = function()
        {
            if( document.readyState == 'complete' )
            {
                onVLCPluginReady();
            }
        }
    }
}

function getVLC(name)
{
    if( window.document[name] )
    {
        return window.document[name];
    }
    if( navigator.appName.indexOf("Microsoft Internet") == -1 )
    {
        if( document.embeds && document.embeds[name] )
            return document.embeds[name];
    }
    else
    {
        return document.getElementById(name);
    }
}

function registerVLCEvent(event, handler)
{
    var vlc = getVLC("vlc");

    if( vlc )
    {
        if( vlc.attachEvent )
        {
            // Microsoft
            vlc.attachEvent(event, handler);
        }
        else if( vlc.addEventListener )
        {
            // Mozilla: DOM level 2
            vlc.addEventListener(event, handler, false);
        }
    }
}

function unregisterVLCEvent(event, handler)
{
    var vlc = getVLC("vlc");

    if( vlc )
    {
        if( vlc.detachEvent )
        {
            // Microsoft
            vlc.detachEvent(event, handler);
        }
        else if( vlc.removeEventListener )
        {
            // Mozilla: DOM level 2
            vlc.removeEventListener(event, handler, false);
        }
    }
}

// JS VLC API callbacks
function handleMediaPlayerMediaChanged()
{
    console.log("!!!vlc Media Changed");
}

function handle_MediaPlayerNothingSpecial()
{
    console.log("!!!vlc Idle...");
}

function handle_MediaPlayerOpening()
{
    console.log("!!!vlc onOpen");
}

function handle_MediaPlayerBuffering(val)
{
    var vlc = getVLC("vlc");
	console.log("!!!vlc  handle_MediaPlayerBuffering("+val+") ");
    if( vlc.playlist.isPlaying )
    {
      onPlaying();
    
    }
}

function handle_MediaPlayerPlaying()
{
     console.log("!!!vlc onPlaying"); 
	 document.getElementById("layer1_cover_vlc").style.opacity="0";
}

function handle_MediaPlayerPaused()
{
    console.log("!!!vlc onPaused");
	document.getElementById("layer1_cover_vlc").style.opacity="1";
}

function handle_MediaPlayerStopped()
{

	console.log("!!!vlc onStop");
	document.getElementById("layer1_cover_vlc").style.opacity="1";
}

function handle_MediaPlayerForward()
{
    console.log("!!!vlc Forward"); 
}

function handle_MediaPlayerBackward()
{
   console.log("!!!vlc Backward");  
}

function handle_MediaPlayerEndReached()
{
     console.log("!!!vlc  onEnd" ); 
}

function handle_MediaPlayerEncounteredError()
{
    console.log("!!!vlc  onError" );
}

function handle_MediaPlayerTimeChanged(time)
{
	//console.log("!!!vlc  TimeChanged" ); 
}

function handle_MediaPlayerPositionChanged(val)
{
 // console.log("!!!vlc  PositionChanged" );
}

function handle_MediaPlayerSeekableChanged(val)
{
   // console.log("!!!vlc  SeekableChanged" );
}

function handle_MediaPlayerPausableChanged(val)
{

	//console.log("!!!vlc  PausableChanged" );
}

function handle_MediaPlayerTitleChanged(val)
{
   // console.log("!!!vlc  TitleChanged" );
}

function handle_MediaPlayerLengthChanged(val)
{
    //console.log("!!!vlc  LengthChanged" );
}

// VLC Plugin
function onVLCPluginReady()
{
    registerVLCEvent("MediaPlayerMediaChanged", handleMediaPlayerMediaChanged);
    registerVLCEvent("MediaPlayerNothingSpecial", handle_MediaPlayerNothingSpecial);
    registerVLCEvent("MediaPlayerOpening", handle_MediaPlayerOpening);
    registerVLCEvent("MediaPlayerBuffering", handle_MediaPlayerBuffering);
    registerVLCEvent("MediaPlayerPlaying", handle_MediaPlayerPlaying);
    registerVLCEvent("MediaPlayerPaused", handle_MediaPlayerPaused);
    registerVLCEvent("MediaPlayerStopped", handle_MediaPlayerStopped);
    registerVLCEvent("MediaPlayerForward", handle_MediaPlayerForward);
    registerVLCEvent("MediaPlayerBackward", handle_MediaPlayerBackward);
    registerVLCEvent("MediaPlayerEndReached", handle_MediaPlayerEndReached);
    registerVLCEvent("MediaPlayerEncounteredError", handle_MediaPlayerEncounteredError);
    registerVLCEvent("MediaPlayerTimeChanged", handle_MediaPlayerTimeChanged);
    registerVLCEvent("MediaPlayerPositionChanged", handle_MediaPlayerPositionChanged);
    registerVLCEvent("MediaPlayerSeekableChanged", handle_MediaPlayerSeekableChanged);
    registerVLCEvent("MediaPlayerPausableChanged", handle_MediaPlayerPausableChanged);
    registerVLCEvent("MediaPlayerTitleChanged", handle_MediaPlayerTitleChanged);
    registerVLCEvent("MediaPlayerLengthChanged", handle_MediaPlayerLengthChanged);
}

function close()
{
    unregisterVLCEvent("MediaPlayerMediaChanged", handleMediaPlayerMediaChanged);
    unregisterVLCEvent("MediaPlayerNothingSpecial", handle_MediaPlayerNothingSpecial);
    unregisterVLCEvent("MediaPlayerOpening", handle_MediaPlayerOpening);
    unregisterVLCEvent("MediaPlayerBuffering", handle_MediaPlayerBuffering);
    unregisterVLCEvent("MediaPlayerPlaying", handle_MediaPlayerPlaying);
    unregisterVLCEvent("MediaPlayerPaused", handle_MediaPlayerPaused);
    unregisterVLCEvent("MediaPlayerStopped", handle_MediaPlayerStopped);
    unregisterVLCEvent("MediaPlayerForward", handle_MediaPlayerForward);
    unregisterVLCEvent("MediaPlayerBackward", handle_MediaPlayerBackward);
    unregisterVLCEvent("MediaPlayerEndReached", handle_MediaPlayerEndReached);
    unregisterVLCEvent("MediaPlayerEncounteredError", handle_MediaPlayerEncounteredError);
    unregisterVLCEvent("MediaPlayerTimeChanged", handle_MediaPlayerTimeChanged);
    unregisterVLCEvent("MediaPlayerPositionChanged", handle_MediaPlayerPositionChanged);
    unregisterVLCEvent("MediaPlayerSeekableChanged", handle_MediaPlayerSeekableChanged);
    unregisterVLCEvent("MediaPlayerPausableChanged", handle_MediaPlayerPausableChanged);
    unregisterVLCEvent("MediaPlayerTitleChanged", handle_MediaPlayerTitleChanged);
    unregisterVLCEvent("MediaPlayerLengthChanged", handle_MediaPlayerLengthChanged);
}


 
function doSetSlider()
{
    var vlc = getVLC("vlc");

    if( vlc && vlc.input.length != 0 )
        vlc.input.time = vlc.input.length / 2;
}

function doGetPosition()
{
    var vlc = getVLC("vlc");

    if( vlc )
        alert( "position is " + vlc.input.position );
}

function doGetTime()
{
    var vlc = getVLC("vlc");

    if( vlc )
        alert( "time is " + vlc.input.time );
}

 

function doAudioChannel(value)
{
    var vlc = getVLC("vlc");
    if( vlc )
        vlc.audio.channel = parseInt(value);
}

function doAudioTrack(value)
{
    var vlc = getVLC("vlc");
    if( vlc )
    {
        var newValue = vlc.audio.track + value;
        if( newValue >= 0 && newValue < vlc.audio.count )
        {
            vlc.audio.track = newValue;
        }
		 alert( " vlc.audio.track is " +  vlc.audio.track);
 
    }
}

 

 
 

 
 
 
function formatTime(timeVal)
{
    if( typeof timeVal != 'number' )
        return "-:--:--";

    var timeHour = Math.round(timeVal / 1000);
    var timeSec = timeHour % 60;
    if( timeSec < 10 )
        timeSec = '0'+timeSec;
    timeHour = (timeHour - timeSec)/60;
    var timeMin = timeHour % 60;
    if( timeMin < 10 )
        timeMin = '0'+timeMin;
    timeHour = (timeHour - timeMin)/60;
    if( timeHour > 0 )
        return timeHour+":"+timeMin+":"+timeSec;
    else
        return timeMin+":"+timeSec;
}

 

/* actions */

function doGo(targetURL)
{
    var vlc = getVLC("vlc");

    if( vlc )
    {
        vlc.playlist.items.clear();
        var options = [":rtsp-tcp"];
        var itemId = vlc.playlist.add(targetURL,"",options);
        if( itemId != -1 )
        {
            // play MRL
            vlc.playlist.playItem(itemId);
        }
        else
        {
            alert("cannot play at the moment !");
        }
        
    }
}


function doPlayOrPause()
{
    var vlc = getVLC("vlc");
    if( vlc )
    {
        if( vlc.playlist.isPlaying )
            vlc.playlist.togglePause();
        else
            vlc.playlist.play();
    }
}

function doStop()
{
    var vlc = getVLC("vlc");
    if( vlc )
        vlc.playlist.stop();
}




function doLogoOption(option, value)
{
    var vlc = getVLC("vlc");
    if( vlc )
    {
        val = parseInt(value);
        switch( option )
        {
            case "1":
                vlc.video.logo.file(value);
                break;
            case "2":
                vlc.video.logo.position = value;
                break;
            case "3":
                vlc.video.logo.opacity = val;
                break;
            case "4":
                vlc.video.logo.repeat = val;
                break;
            case "5":
                vlc.video.logo.delay = val;
                break;
            case "6":
                vlc.video.logo.x = val;
                break;
            case "7":
                vlc.video.logo.y = val;
                break;
        }
    }
}

 

/* events */
 


function onPlaying()
{
    var vlc = getVLC("vlc");
    
    if( vlc )
    {
        var mediaLen = vlc.input.length;
        if( mediaLen > 0 )
        {
            // seekable media
            console.log("!!!vlc seekable media"+ formatTime(vlc.input.time)+"/"+formatTime(mediaLen) );
        }
        else
        {
            // 
			 console.log("!!!vlc non-seekable live media" );
        }
    }
}


 

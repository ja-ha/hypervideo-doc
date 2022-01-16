using System.Collections;
using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.Video;

public class VideoPlayerHandler : MonoBehaviour
{
    // Video map variables
    public string mapFileName;
    private Dictionary<string, Dictionary<string, string>> _map;
    
    // Name of the fallback missing video file
    public string missingVideoName;
    
    // Video FPS
    public int VideoFPS;
    
    // Video player variables
    public VideoPlayer currentPlayer;
    public VideoPlayer defPlayer;
    public VideoPlayer altPlayer;

    // Video segment variables
    private string _current;
    private string _def;
    private string _alt;
    
    // Start is called before the first frame update
    IEnumerator Start()
    {
        // Set framerate to video framerate to avoid blank frames
        Application.targetFrameRate = VideoFPS;
        
        // Load video map
        var mapFilePath = Path.Combine(Application.streamingAssetsPath, mapFileName);
        string mapFileJson = null;
        
        // Check if we are on the web
        if (mapFilePath.Contains("://") || mapFilePath.Contains(":///"))
        {
            using (UnityWebRequest webRequest = UnityWebRequest.Get(mapFilePath))
            {
                // Request and wait for the desired ressource.
                yield return webRequest.SendWebRequest();

                string[] pages = mapFilePath.Split('/');
                int page = pages.Length - 1;

                switch (webRequest.result)
                {
                    case UnityWebRequest.Result.ConnectionError:
                    case UnityWebRequest.Result.DataProcessingError:
                        Debug.LogError(pages[page] + ": Error: " + webRequest.error);
                        break;
                    case UnityWebRequest.Result.ProtocolError:
                        Debug.LogError(pages[page] + ": HTTP Error: " + webRequest.error);
                        break;
                    case UnityWebRequest.Result.Success:
                        Debug.Log(pages[page] + ":\nReceived: " + webRequest.downloadHandler.text);
                        mapFileJson = webRequest.downloadHandler.text;
                        break;
                }
            }
        }
        else
        {
            // If not on web, access file using System.IO
            mapFileJson = File.ReadAllText(mapFilePath);
        }
            

        // Deserialize json data for video map
        _map = JsonConvert.DeserializeObject<Dictionary<string, Dictionary<string, string>>>(mapFileJson);
        
        // Setup initial play by using the special "ENTRYPOINT" key in the video map
        _current = GETVideoStrings("ENTRYPOINT").Item1;
        
        // Set path and start current video playback
        currentPlayer.url = UrlFor(_current);
        currentPlayer.Play();

        // Setup actual default and alt video play
        SetupVideo();
        
        // Set path and prepare onClick (alt) video Playback
        altPlayer.Prepare();
        
        // Setup default playback for all players
        currentPlayer.loopPointReached += EndReached;
        defPlayer.loopPointReached += EndReached;
        altPlayer.loopPointReached += EndReached;
    }
    
    // Update is called once per frame
    void Update()
    {
        // Check if default player is not prepared yet and current video will end in less than 3 seconds
        if(!defPlayer.isPrepared && currentPlayer.frame + 200f > currentPlayer.frameCount)
        {
            defPlayer.Prepare();
            Debug.Log("Told defPlayer to Prepare...");
        }
    }

    // EndReached is called by a video player reaching the end of a clip
    void EndReached(VideoPlayer _)
    {
        Debug.Log("End of clip reached");
        
        // Stop all other video playback, start default video playback
        currentPlayer.Stop();
        defPlayer.Play();
        altPlayer.Stop();
        
        // Both players switch roles
        (currentPlayer, defPlayer) = (defPlayer, currentPlayer);
            
        // Setup new alt and default players
        _current = _def;
        SetupVideo();
            
        Debug.Log("Now Playing: " + _current);
    }
    
    // OnClick is called by the Input System
    void OnClick()
    {
        Debug.Log("Click registered");
        
        // Stop all other video playback, start alt video playback
        defPlayer.Stop();
        currentPlayer.Stop();
        altPlayer.Play();
        
        // Both players switch roles
        (currentPlayer, altPlayer) = (altPlayer, currentPlayer);
        
        // Setup new alt and default players
        _current = _alt;
        SetupVideo();
        
        Debug.Log("Now Playing: " + _current);
    }

    void SetupVideo()
    {
        // Get default and alt videos for currently playing node
        (_def, _alt) = GETVideoStrings(_current);
        
        // Set default and alt Player URLs
        defPlayer.url = UrlFor(_def);
        altPlayer.url = UrlFor(_alt);
        
        // Tell alt Player to prepare for Playback
        altPlayer.Prepare();
        Debug.Log("Told altPlayer to Prepare...");
    }
    
    // Fetches Video clip names from video node map
    (string, string) GETVideoStrings(string video)
    {
        // Get node from map by name, if not found, return missing video clip name
        if (!_map.TryGetValue(video, out var node)) return (missingVideoName, missingVideoName);
        
        if (node.TryGetValue("def", out var def)) {}
        else
        {
            // if not found, use missing clip string
            def = missingVideoName;
        }
            
        if (node.TryGetValue("alt", out var alt)) {}
        else
        {
            alt = missingVideoName;
        }

        return (def, alt);

    }

    // Combines Streaming Path, video clip name and extension
    string UrlFor(string video)
    {
        return Path.Combine(Application.streamingAssetsPath, video + ".mp4");
    }
}
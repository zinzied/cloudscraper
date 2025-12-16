import re
import json
import time
import requests
from .lz_string_custom import CustomLZString
from .user_agent import User_Agent

# Ported from constants.go
BROWSER_CONFIGURATION = {
    "0": [
        "length", "innerWidth", "innerHeight", "scrollX", "pageXOffset", "scrollY", "pageYOffset", 
        "screenX", "screenY", "screenLeft", "screenTop", "TEMPORARY", "n.maxTouchPoints"
    ],
    "1": [
        "devicePixelRatio", "PERSISTENT", "d.childElementCount", "d.ELEMENT_NODE", 
        "d.DOCUMENT_POSITION_DISCONNECTED"
    ],
    "2": ["d.ATTRIBUTE_NODE", "d.DOCUMENT_POSITION_PRECEDING"],
    "3": ["d.TEXT_NODE"],
    "4": ["d.CDATA_SECTION_NODE", "d.DOCUMENT_POSITION_FOLLOWING"],
    "5": ["d.ENTITY_REFERENCE_NODE"],
    "6": ["d.ENTITY_NODE"],
    "7": ["d.PROCESSING_INSTRUCTION_NODE"],
    "8": ["n.deviceMemory", "d.COMMENT_NODE", "d.DOCUMENT_POSITION_CONTAINS"],
    "9": ["d.nodeType", "d.DOCUMENT_NODE"],
    "10": ["d.DOCUMENT_TYPE_NODE"],
    "11": ["d.DOCUMENT_FRAGMENT_NODE"],
    "12": ["n.hardwareConcurrency", "d.NOTATION_NODE"],
    "16": ["d.DOCUMENT_POSITION_CONTAINED_BY"],
    "32": ["d.DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC"],
    "1032": ["outerHeight"],
    "1920": ["outerWidth"],
    "o": [
        "window", "self", "document", "location", "customElements", "history", "navigation", 
        "locationbar", "menubar", "personalbar", "scrollbars", "statusbar", "toolbar", "frames", 
        "top", "parent", "frameElement", "navigator", "external", "screen", "visualViewport", 
        "clientInformation", "styleMedia", "trustedTypes", "performance", "crypto", "indexedDB", 
        "sessionStorage", "localStorage", "scheduler", "chrome", "caches", "cookieStore", 
        "launchQueue", "speechSynthesis", "globalThis", "JSON", "Math", "Intl", "Atomics", 
        "Reflect", "console", "CSS", "WebAssembly", "GPUBufferUsage", "GPUColorWrite", 
        "GPUMapMode", "GPUShaderStage", "GPUTextureUsage", "n.scheduling", "n.userActivation", 
        "n.geolocation", "n.connection", "n.plugins", "n.mimeTypes", "n.webkitTemporaryStorage", 
        "n.webkitPersistentStorage", "n.bluetooth", "n.clipboard", "n.credentials", "n.keyboard", 
        "n.managed", "n.mediaDevices", "n.storage", "n.serviceWorker", "n.virtualKeyboard", 
        "n.wakeLock", "n.ink", "n.hid", "n.locks", "n.mediaCapabilities", "n.mediaSession", 
        "n.permissions", "n.presentation", "n.serial", "n.gpu", "n.usb", "n.windowControlsOverlay", 
        "n.xr", "n.userAgentData", "d.location", "d.implementation", "d.documentElement", 
        "d.body", "d.head", "d.images", "d.embeds", "d.plugins", "d.links", "d.forms", "d.scripts", 
        "d.defaultView", "d.anchors", "d.applets", "d.scrollingElement", "d.featurePolicy", 
        "d.children", "d.firstElementChild", "d.lastElementChild", "d.activeElement", 
        "d.styleSheets", "d.fonts", "d.fragmentDirective", "d.timeline", "d.childNodes", 
        "d.firstChild", "d.lastChild"
    ],
    "false": [
        "closed", "crossOriginIsolated", "credentialless", "originAgentCluster", "n.webdriver", 
        "d.xmlStandalone", "d.hidden", "d.wasDiscarded", "d.prerendering", "d.webkitHidden", 
        "d.fullscreen", "d.webkitIsFullScreen"
    ],
    "x": [
        "opener", "onsearch", "onappinstalled", "onbeforeinstallprompt", "onbeforexrselect", 
        "onabort", "onbeforeinput", "onblur", "oncancel", "oncanplay", "oncanplaythrough", 
        "onchange", "onclick", "onclose", "oncontextlost", "oncontextmenu", "oncontextrestored", 
        "oncuechange", "ondblclick", "ondrag", "ondragend", "ondragenter", "ondragleave", 
        "ondragover", "ondragstart", "ondrop", "ondurationchange", "onemptied", "onended", 
        "onerror", "onfocus", "onformdata", "oninput", "oninvalid", "onkeydown", "onkeypress", 
        "onkeyup", "onload", "onloadeddata", "onloadedmetadata", "onloadstart", "onmousedown", 
        "onmouseenter", "onmouseleave", "onmousemove", "onmouseout", "onmouseover", "onmouseup", 
        "onmousewheel", "onpause", "onplay", "onplaying", "onprogress", "onratechange", "onreset", 
        "onresize", "onscroll", "onsecuritypolicyviolation", "onseeked", "onseeking"
    ]
}

class JSDSolver:
    def __init__(self, user_agent=None):
        self.user_agent = user_agent
        self.lz_key_regex = re.compile(r'[^\s,]*\$[^\s,]*\+?[^\s,]*')
        self.s_key_regex = re.compile(r'\d+\.\d+:\d+:[^\s,]+')

    def parse_script(self, content):
        found_lz_key = self.lz_key_regex.findall(content)
        found_s_key = self.s_key_regex.findall(content)

        if len(found_lz_key) == 2 and len(found_s_key) == 2:
            lz_key = found_lz_key[1]
            if "+" not in lz_key:
                lz_key = found_lz_key[0]
            
            # Clean up the keys (remove potential wrapping quotes or trailing chars captured by greedy regex)
            # The regex [^\s,]* matches everything until a space or comma. 
            # This often includes surrounding quotes or semicolons in JS.
            lz_key = lz_key.strip("\"\';")
            s_key = found_s_key[1].strip("\"\';")
            
            return lz_key, s_key
        
        return None, None

    def build_payload(self, user_agent):
        payload_data = BROWSER_CONFIGURATION.copy()
        payload_data["APPVERSION"] = user_agent.replace("Mozilla/", "")
        payload_data["USERAGENT"] = user_agent
        # This specific key format "MM/DD/YYYY HH:MM:SS" is from the reference repo
        # Ideally this should probably be dynamically set or is a specific fingerprint key
        # The Go code uses "06/26/2023 06:47:34" as a constant key name? 
        # Yes: p.Data["06/26/2023 06:47:34"] = time.Now().Format("01/02/2006 15:04:05")
        # Go's time layout is weird, "01/02/2006 15:04:05" means MM/DD/YYYY HH:MM:SS
        payload_data["06/26/2023 06:47:34"] = time.strftime("%m/%d/%Y %H:%M:%S")
        return payload_data

    def solve(self, script_content, user_agent=None):
        if not user_agent:
            user_agent = self.user_agent
        
        lz_key, secret_key = self.parse_script(script_content)
        if not lz_key or not secret_key:
            raise ValueError("Could not parse keys from JSD script.")

        payload_data = self.build_payload(user_agent)
        payload_json = json.dumps(payload_data, separators=(',', ':')) # Minimize standard storage
        
        # Compress
        # Reference: windowProperties, err := new(LZString).CompressToEncodedURIComponent(c.Payload, lzStringKey)
        custom_lz = CustomLZString()
        window_properties = custom_lz.compress_to_encoded_uri_component(payload_json, lz_key)
        
        return {
            "wp": window_properties,
            "s": secret_key
        }

    # Example method to actually perform the request if integrated directly
    # Ideally this logic belongs in the main CloudScraper class or a requester
    def solve_and_get_request_data(self, script_content, ray_id, user_agent):
        solution = self.solve(script_content, user_agent)
        
        # The submission URL is traditionally:
        # /cdn-cgi/challenge-platform/h/g/jsd/r/{ray_id}
        
        return {
            "url_path_suffix": f"/cdn-cgi/challenge-platform/h/g/jsd/r/{ray_id}",
            "json_payload": solution
        }

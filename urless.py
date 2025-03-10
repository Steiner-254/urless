#!/usr/bin/env python
# Python 3
# urless - by @Xnl-h4ck3r: De-clutter a list of URLs
# Full help here: https://github.com/xnl-h4ck3r/urless/blob/main/README.md
# Good luck and good hunting! If you really love the tool (or any others), or they helped you find an awesome bounty, consider BUYING ME A COFFEE! (https://ko-fi.com/xnlh4ck3r) ☕ (I could use the caffeine!)

from ast import arg
import re
import os
import sys
from typing import Pattern
import yaml
import argparse
from signal import SIGINT, signal
from urllib.parse import urlparse
from termcolor import colored
from pathlib import Path

# Default values if config.yml not found
DEFAULT_FILTER_EXTENSIONS = '.css,.ico,.jpg,.jpeg,.png,.bmp,.svg,.img,.gif,.mp4,.flv,.ogv,.webm,.webp,.mov,.mp3,.m4a,.m4p,.scss,.tif,.tiff,.ttf,.otf,.woff,.woff2,.bmp,.ico,.eot,.htc,.rtf,.swf,.image'
DEFAULT_FILTER_KEYWORDS = 'blog,article,news,bootstrap,jquery,captcha,node_modules'
DEFAULT_LANGUAGE = 'en,en-us,en-gb,fr,de,pl,nl,fi,sv,it,es,pt,ru,pt-br,es-mx,zh-tw,js.ko,gb-en,ca-en,au-en,fr-fr,ca-fr,es-es,mx-es,de-de,it-it,br-pt,pt-pt,jp-ja,cn-zh,tw-zh,kr-ko,sa-ar,in-hi,ru-ru'

# Variables to hold config.yml values
FILTER_EXTENSIONS = ''
FILTER_KEYWORDS = ''
LANGUAGE = ''

# Regex delimiters
REGEX_START = '^'
REGEX_END = '$'

# Regex for a path folder of integer
REGEX_INTEGER = REGEX_START + '\d+' + REGEX_END
reIntPart = re.compile(REGEX_INTEGER)
patternsInt = {}

# Regex for a path folder of GUID
REGEX_GUID = REGEX_START + '[({]?[a-fA-F0-9]{8}[-]?([a-fA-F0-9]{4}[-]?){3}[a-fA-F0-9]{12}[})]?' + REGEX_END
reGuidPart = re.compile(REGEX_GUID)
patternsGUID = {}

# Regex fields for Custom ID
reCustomIDPart = Pattern
patternsCustomID = {}

# Regex for path of YYYY/MM
REGEX_YYYYMM = '\/[1|2][0|1|9]\\d{2}/[0|1]\\d{1}\/'
reYYYYMM = re.compile(REGEX_YYYYMM)

# Regex for path of language code
reLangPart = Pattern
patternsLang = {}

# Global variables
args = None
urlmap = {}
patternsSeen = []
outFile = None
linesOrigCount = 0
linesFinalCount = 0

def verbose():
    '''
    Functions used when printing messages dependant on verbose option
    '''
    return args.verbose

def write(text='',pipe=False):
    # Only send text to stdout if the tool isn't piped to pass output to something else, 
    # or if the tool has been piped and the pipe parameter is True
    if sys.stdout.isatty() or (not sys.stdout.isatty() and pipe):
        sys.stdout.write(text+'\n')

def writerr(text=''):
    # Only send text to stdout if the tool isn't piped to pass output to something else, 
    # or If the tool has been piped to output the send to stderr
    if sys.stdout.isatty():
        sys.stdout.write(text+'\n')
    else:
        sys.stderr.write(text+'\n')
            
def showBanner():
    write('')
    write(colored('  __  _ ____  _   ___  ___ ____ ', 'red'))
    write(colored(' | | | |  _ \| | / _ \/ __/ __/ ', 'yellow'))
    write(colored(' | | | | |_) | ||  __/\__ \__ \ ', 'green'))
    write(colored(' | |_| |  _ <| |_\___/\___/___/ ', 'cyan'))
    write(colored('  \___/|_| \_\___/', 'magenta')+colored('by Xnl-h4ck3r','white'))
    write('')

def getConfig():
    '''
    Try to get the values from the config file, otherwise use the defaults
    '''
    global FILTER_EXTENSIONS, FILTER_KEYWORDS, LANGUAGE, reLangPart
    try:

        # Try to get the config file values
        try:        
            urlessPath = Path(
                os.path.dirname(os.path.realpath(__file__))
            )
            urlessPath.absolute
            if urlessPath == '':
                configPath = 'config.yml'
            else:
                configPath = Path(urlessPath / 'config.yml')
            config = yaml.safe_load(open(configPath))
            
            # If the user provided the --filter-extensions argument then it overrides the config value
            if args.filter_keywords:
                FILTER_KEYWORDS = args.filter_keywords
            else:
                try:
                    FILTER_KEYWORDS = config.get('FILTER_KEYWORDS')
                    if str(FILTER_KEYWORDS) == 'None':
                        writerr(colored('No value for FILTER_KEYWORDS in config.yml - default set', 'yellow'))
                        FILTER_KEYWORDS = ''
                except Exception as e:
                    writerr(colored('Unable to read FILTER_EXTENSIONS from config.yml - default set', 'red'))
                    FILTER_KEYWORDS = DEFAULT_FILTER_KEYWORDS
            
            # If the user provided the --filter-extensions argument then it overrides the config value
            if args.filter_extensions:
                FILTER_EXTENSIONS = args.filter_extensions
            else:    
                try:
                    FILTER_EXTENSIONS = config.get('FILTER_EXTENSIONS')
                    if str(FILTER_EXTENSIONS) == 'None':
                        writerr(colored('No value for FILTER_EXTENSIONS in config.yml - default set', 'yellow'))
                        FILTER_EXTENSIONS = ''
                except Exception as e:
                    writerr(colored('Unable to read FILTER_EXTENSIONS from config.yml - default set', 'red'))
                    FILTER_EXTENSIONS = DEFAULT_FILTER_EXTENSIONS
            
            # If the user provided the --language argument then create the regex for language codes
            if args.language:  
                # Get the language codes
                try:
                    LANGUAGE = config.get('LANGUAGE')
                    if str(LANGUAGE) == 'None':
                        writerr(colored('No value for LANGUAGE in config.yml - default set', 'yellow'))
                        LANGUAGE = ''
                except Exception as e:
                    writerr(colored('Unable to read LANGUAGE from config.yml - default set', 'red'))
                    LANGUAGE = DEFAULT_LANGUAGE
                # Set the language regex
                try:
                    reLangPart = re.compile(REGEX_START + '(' + LANGUAGE.replace(',','|') + ')' + REGEX_END)    
                except Exception as e:
                    writerr(colored('ERROR getConfig 2: ' + str(e), 'red'))
                    
        except:
            writerr(colored('WARNING: Cannot find config.yml, so using default values', 'yellow'))
            FILTER_EXTENSIONS = DEFAULT_FILTER_EXTENSIONS
            FILTER_KEYWORDS = DEFAULT_FILTER_KEYWORDS
            LANGUAGE = DEFAULT_LANGUAGE
            
    except Exception as e:
        writerr(colored('ERROR getConfig 1: ' + str(e), 'red'))

def handler(signal_received, frame):
    '''
    This function is called if Ctrl-C is called by the user
    An attempt will be made to try and clean up properly
    '''
    writerr(colored('>>> "Oh my God, they killed Kenny... and urless!" - Kyle', 'red'))
    sys.exit()
                        
def paramsToDict(params: str) -> list:
    '''
    converts query string to dict
    '''
    try:
        the_dict = {}
        if params:
            for pair in params.split('&'):
                # If there is a parameter but no = then add a value of {EMPTY}
                if pair.find('=') < 0:
                    key = pair+'{EMPTY}'
                    the_dict[key] = '{EMPTY}'
                else:
                    parts = pair.split('=')
                    try:
                        the_dict[parts[0]] = parts[1]
                    except IndexError:
                        pass
        return the_dict
    except Exception as e:
        writerr(colored('ERROR paramsToDict 1: ' + str(e), 'red'))

def dictToParams(params: dict) -> str:
    '''
    converts dict of params to query string
    '''
    try:
        # If a parameter has a value of {EMPTY} then just the name will be written and no =
        stringed = [name if value == '{EMPTY}' else name + '=' + value for name, value in params.items()]

        # Only add a ? at the start of parameters, unless the first starts with #
        if list(params.keys())[0][:1] == '#':
            paramString = ''.join(stringed)
        else:
            paramString = '?' + '&'.join(stringed)

        # If a there are any parameters with {EMPTY} in the name then remove the string
        return paramString.replace('{EMPTY}','')
    except Exception as e:
        writerr(colored('ERROR dictToParams 1: ' + str(e), 'red'))

def compareParams(currentParams: list, newParams: dict) -> bool:
    '''
    checks if newParams contain a param
    that doesn't exist in currentParams
    '''
    try:
        ogSet = set([])
        for each in currentParams:
            for key in each.keys():
                ogSet.add(key)
        return set(newParams.keys()) - ogSet
    except Exception as e:
        writerr(colored('ERROR compareParams 1: ' + str(e), 'red'))
        
def isUnwantedContent(path: str) -> bool:
    '''
    Checks any potentially unwanted patterns (unless specified otherwise) such as blog/news content
    '''
    try:
        unwanted = False
        
        if not args.keep_human_written:
            # If the path has more than 3 dashes '-' AND isn't a GUID AND (if specified) isn't a Custom ID, then assume it's human written content, e.g. blog
            for part in path.split('/'):
                if part.count('-') > 3:
                    if str(reCustomIDPart.pattern) == '':
                        if not reGuidPart.search(part) and reCustomIDPart.search(part):
                            unwanted = True
                    else:
                        if not reGuidPart.search(part):
                            unwanted = True
        
        if not args.keep_yyyymm:
            # If it contains a year and month in the path then assume like blog/news content, r.g. .../2019/06/...
            if reYYYYMM.search(path):
                unwanted = True
            
        return unwanted
    except Exception as e:
        writerr(colored('ERROR isUnwantedContent 1: ' + str(e), 'red'))

def createPattern(path: str) -> str:
    '''
    creates patterns for urls with integers or GUIDs in them
    '''
    global patternsGUID, patternsInt, patternsCustomID, patternsLang
    try:
        newParts = []

        regexInt = False
        regexGUID = False
        regexCustom = False
        regexLang = False
        for part in path.split('/'):
            if part == '':
                newParts.append(part)
            elif str(reCustomIDPart.pattern) != '' and reCustomIDPart.search(part):
                regexCustom = True
                newParts.append(reCustomIDPart.pattern)
            elif reGuidPart.search(part):
                regexGUID = True
                newParts.append(reGuidPart.pattern)
            elif reIntPart.match(part):
                regexInt = True
                newParts.append(reIntPart.pattern)
            elif args.language and reLangPart.match(part.lower()):
                regexLang = True
                newParts.append(reLangPart.pattern)
            else:
                newParts.append(part)
        createdPattern = '/'.join(newParts)
        
        # Depending on the type of regex, add the found pattern to the dictionary if it hasn't been added already
        if regexCustom and createdPattern not in patternsCustomID:
            patternsCustomID[createdPattern] = path
        elif regexGUID and createdPattern not in patternsGUID:
            patternsGUID[createdPattern] = path
        elif regexInt and createdPattern not in patternsInt:
            patternsInt[createdPattern] = path
        elif regexLang and createdPattern not in patternsLang:
            patternsLang[createdPattern] = path
            
        return createdPattern
    except Exception as e:
        writerr(colored('ERROR createPattern 1: ' + str(e), 'red'))

def patternExists(pattern: str) -> bool:
    '''
    Checks if a pattern exists
    '''
    try:
        for i, seen_pattern in enumerate(patternsSeen):
            if pattern == seen_pattern:
                patternsSeen[i] = pattern
                return True
            elif seen_pattern in pattern:
                return True
        return False
    except Exception as e:
        writerr(colored('ERROR patternExists 1: ' + str(e), 'red'))

def matchesPatterns(path: str) -> bool:
    '''
    checks if the url matches any of the regex patterns
    '''
    try:
        for pattern in patternsSeen:
            if re.search(pattern, re.escape(path)) is not None:
                return True
        return False
    except Exception as e:
        writerr(colored('ERROR matchesPatterns 1: ' + str(e), 'red'))

def hasFilterKeyword(path: str) -> bool:
    '''
    checks if the url matches the blacklist regex
    '''
    global FILTER_KEYWORDS
    try:
        return re.search(FILTER_KEYWORDS.replace(',','|'), path, re.IGNORECASE)
    except Exception as e:
        writerr(colored('ERROR hasFilterKeyword 1: ' + str(e), 'red'))

def hasBadExtension(path: str) -> bool:
    '''
    checks if a url has a blacklisted extension
    '''
    global FILTER_EXTENSIONS
    try:
        badExtension = False
        if '/' not in path.split('.')[-1]:
            extensions = FILTER_EXTENSIONS.split(',')
            for extension in extensions:
                if path.lower().endswith(extension.lower()):
                    badExtension = True
        return badExtension
    except Exception as e:
        writerr(colored('ERROR hasBadExtension 1: ' + str(e), 'red'))

def processUrl(line):
    
    try:
        parsed = urlparse(line.strip())
        
        # Set the host
        scheme = parsed.scheme
        if scheme == '':
            host = parsed.netloc
        else:
            host = scheme + '://' + parsed.netloc
            
        # If the link specifies port 80 or 443, e.g. http://example.com:80, then remove the port
        if str(parsed.port) == '80':
            host = host.replace(':80','',1)
        if str(parsed.port) == '443':
            host = host.replace(':443','',1)
            
        # Build the path and parameters
        path, params = parsed.path, paramsToDict(parsed.query)

        # If there is a fragment, add as the last parameter with a name but with value {EMPTY} that doesn't add an = afterwards
        if parsed.fragment:
            params['#'+parsed.fragment] = '{EMPTY}'
        
        # Add the host to the map if it hasn't already been seen
        if host not in urlmap:
            urlmap[host] = {}
        
        # If the path has an extension we want to exclude, then just return to continue with the next line   
        if hasBadExtension(path):
            return
        
        # If the are no parameters and path isn't empty
        if not params and path != "":
            
            # If its unwanted content or has a keyword to be excluded, then just return to continue with the next line
            if isUnwantedContent(path) or hasFilterKeyword(path):
                return
            
            # If the current path already matches a previously saved pattern then just return to continue with the next line
            if matchesPatterns(path):
                return
            
        # If the path has ++ in it for any reason, then just output "as is" otherwise it will raise a regex Multiple Repeat Error
        if path.find('++') > 0:
            pattern = path
        else:
            # Create a pattern for the current path
            pattern = createPattern(path)
            
        # Update the url map
        if pattern not in urlmap[host]:
            urlmap[host][pattern] = [params] if params else []
        elif params and compareParams(urlmap[host][pattern], params):
            urlmap[host][pattern].append(params)

    except ValueError as ve:
        if verbose():
            writerr(colored('This URL caused a Value Error and was not included: ' + line, 'red'))
    except Exception as e:
        writerr(colored('ERROR processUrl 1: ' + str(e), 'red'))
        
def processLine(line):
    '''
    Process a line from the input based on whether the -ks / --keep-slash argument was passed 
    '''
    # If the -ks / --keep-slash argument was passed, then just add all URLs, 
    # else remove the trailing slash form any URLs (before any query string)
    if args.keep_slash:
        line = line.rstrip('\n')
    else:
        if line.find('/?') > 0:
            line = line.replace('/?','?',1)
        else:
            line = line.rstrip('\n').rstrip('/')
            
    # If the -iq / --ignore-querystring argument was passed, remove any querystring and fragment
    if args.ignore_querystring:
        line = line.split('?')[0].split('#')[0]
    return line
                            
def processInput():
    
    global linesOrigCount
    try:
        if not sys.stdin.isatty():
            for line in sys.stdin:
                processUrl(processLine(line))
        else:
            try:
                inFile = open(os.path.expanduser(args.input), 'r')
                lines = inFile.readlines()
                linesOrigCount = len(lines)
                for line in lines:
                    processUrl(processLine(line))
            except Exception as e:
                writerr(colored('ERROR processInput 2 ' + str(e), 'red'))    
            
            try:
                inFile.close()
            except:
                pass            
    except Exception as e:
        writerr(colored('ERROR processInput 1: ' + str(e), 'red'))   
        
def processOutput():
    global linesFinalCount, linesOrigCount, patternsGUID, patternsInt, patternsCustomID, patternsLang
    try:
        # If an output file was specified, open it
        if args.output is not None:
            try:
                outFile = open(os.path.expanduser(args.output), 'w')
            except Exception as e:
                writerr(colored('ERROR processOutput 2 ' + str(e), 'red'))   

        # Output all URLs    
        for host, value in urlmap.items():
            for path, params in value.items():

                # Replace the regex pattern in the path with the first occurrence of that pattern found
                try:
                    customRegexFound = False
                    if str(reCustomIDPart.pattern) != '' and path.find(str(reCustomIDPart.pattern)) > 0:
                        for pattern in patternsCustomID:
                            if pattern == path:
                                path = patternsCustomID[pattern]
                                customRegexFound = True
                    if not customRegexFound:
                        if path.find(REGEX_GUID) > 0:
                            for pattern in patternsGUID:
                                if pattern == path:
                                    path = patternsGUID[pattern]
                        elif path.find(REGEX_INTEGER) > 0:
                            for pattern in patternsInt:
                                if pattern == path:
                                    path = patternsInt[pattern]
                        elif path.find(str(reLangPart.pattern)) > 0:
                            for pattern in patternsLang:
                                if pattern == path:
                                    path = patternsLang[pattern]
                except Exception as e:
                    writerr(colored('ERROR processOutput 4: ' + str(e), 'red'))
                    
                if params:
                    for param in params:
                        linesFinalCount = linesFinalCount + 1
                        # If an output file was specified, write to the file
                        if args.output is not None:
                            outFile.write(host + path + dictToParams(param) + '\n')
                        else:    
                            # If output is piped or the --output argument was not specified, output to STDOUT
                            if not sys.stdin.isatty() or args.output is None:
                                write(host + path + dictToParams(param),True)
                else:
                    linesFinalCount = linesFinalCount + 1
                    # If an output file was specified, write to the file
                    if args.output is not None:
                        outFile.write(host + path + '\n')
                    else:    
                        # If output is piped or the --output argument was not specified, output to STDOUT
                        if not sys.stdin.isatty() or args.output is None:
                            write(host + path,True)
        
        if verbose() and sys.stdin.isatty():
            writerr(colored('\nInput reduced from '+str(linesOrigCount)+' to '+str(linesFinalCount)+' lines 🤘', 'cyan'))
            
        # Close the output file if it was opened
        try:
            if args.output is not None:
                write(colored('Output successfully written to file: ', 'cyan')+colored(args.output,'white'))
                write()
                outFile.close()
        except Exception as e:
            writerr(colored('ERROR processOutput 3: ' + str(e), 'red'))
                            
    except Exception as e:
        writerr(colored('ERROR processOutput 1: ' + str(e), 'red'))

def showOptionsAndConfig():
    global FILTER_EXTENSIONS, FILTER_KEYWORDS, LANGUAGE
    try:
        write(colored('Selected options and config:', 'cyan'))
        write(colored('-i: ' + args.input, 'magenta')+colored(' The input file of URLs to de-clutter.','white'))
        if args.output is not None:
            write(colored('-o: ' + args.output, 'magenta')+colored(' The output file that the de-cluttered URL list will be written to.','white'))
        else:
            write(colored('-o: <STDOUT>', 'magenta')+colored(' An output file wasn\'t given, so output will be written to STDOUT.','white'))
            
        if args.filter_keywords:
            write(colored('-fk (Keywords to Filter): ', 'magenta')+colored(args.filter_keywords,'white'))
        else:
            write(colored('Filter Keywords (from Config.yml): ', 'magenta')+colored(FILTER_KEYWORDS,'white'))
        
        if args.filter_extensions:
            write(colored('-fe (Extensions to Filter): ', 'magenta')+colored(args.filter_extensions,'white'))
        else:
            write(colored('Filter Extensions (from Config.yml): ', 'magenta')+colored(FILTER_EXTENSIONS,'white'))
        
        if args.language:
            write(colored('Languages (from Config.yml): ', 'magenta')+colored(LANGUAGE,'white'))
            write(colored('-lang: True', 'magenta')+colored('If there are multiple URLs with different language codes as a part of the path, only one version of the URL will be output.','white'))
            
        if args.keep_slash:
            write(colored('-ks: True', 'magenta')+colored('A trailing slash at the end of a URL in input will not be removed. Therefore there may be identical URLs output, one with and one without a trailing slash.','white'))
        
        if args.keep_human_written:
            write(colored('-khw: True', 'magenta')+colored('Prevent URLs with a path part that contains 3 or more dashes (-) from being removed (e.g. blog post)','white'))
            
        if args.keep_yyyymm:
            write(colored('-kym: True', 'magenta')+colored('Prevent URLs with a path part that contains a year and month in the format `/YYYY/DD` (e.g. blog or news)','white'))
            
        if args.regex_custom_id:
            write(colored('-rcid: \'' + str(reCustomIDPart.pattern) + '\'', 'magenta')+colored(' USE WITH CAUTION! ','red')+colored('Regex for a Custom ID that your target uses. Ensure the value is passed in quotes. See the README for more details on this.','white'))
        
        if args.keep_yyyymm:
            write(colored('-iq: True', 'magenta')+colored(' Remove the query string (including URL fragments `#`) so output is unique paths only.','white'))

        write('')
        
    except Exception as e:
        writerr(colored('ERROR showOptionsAndConfig 1: ' + str(e), 'red'))    

def argCheckRegexCustomID(value):
    global reCustomIDPart
    try:
        
         # If the Custom ID regex was passed, then prefix with ^ and suffix with $ if they are not there already
        if value != '':
            if value[0] != REGEX_START:
                value = REGEX_START + value
            if value[-1] != REGEX_END:
                value = value + REGEX_END
        
        # Try to compile the regex
        reCustomIDPart = re.compile(value)
        
        return value
    except:
        raise argparse.ArgumentTypeError(
            'Valid regex must be passed.'
        )
                        
def main():
    
    global args, urlmap, patternsSeen, patternsInt, patternsCustomID, patternsGUID, patternsLang
    
    # Tell Python to run the handler() function when SIGINT is received
    signal(SIGINT, handler)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='urless - by @Xnl-h4ck3r: De-clutter a list of URLs.'    
    )
    parser.add_argument(
        '-i',
        '--input',
        action='store',
        help='A file of URLs to de-clutter.'
    )
    parser.add_argument(
        '-o',
        '--output',
        action='store',
        help='The output file that will contain the de-cluttered list of URLs (default: output.txt). If piped to another program, output will be written to STDOUT instead.',
    )
    parser.add_argument(
        '-fk',
        '--filter_keywords',
        action='store',
        help='A comma separated list of keywords to exclude links (if there no parameters). This will override the FILTER_KEYWORDS list specified in config.yml',
        metavar='<comma separated list>'
    )
    parser.add_argument(
        '-fe',
        '--filter-extensions',
        action='store',
        help='A comma separated list of file extensions to exclude. This will override the FILTER_EXTENSIONS list specified in config.yml',
        metavar='<comma separated list>'
    )
    parser.add_argument(
        '-ks',
        '--keep-slash',
        action='store_true',
        help='A trailing slash at the end of a URL in input will not be removed. Therefore there may be identical URLs output, one with and one without a trailing slash.',
    )
    parser.add_argument(
        '-khw',
        '--keep-human-written',
        action='store_true',
        help='By default, any URL with a path part that contains 3 or more dashes (-) are removed because it is assumed to be human written content (e.g. blog post) and not interesting. Passing this argument will keep them in the output.',
    )
    parser.add_argument(
        '-kym',
        '--keep-yyyymm',
        action='store_true',
        help='By default, any URL with a path containing 3 /YYYY/MM (where YYYY is a year and MM month) are removed because it is assumed to be blog/news content, and not interesting. Passing this argument will keep them in the output.',
    )
    parser.add_argument(
        '-rcid',
        '--regex-custom-id',
        action='store',
        help='USE WITH CAUTION! Regex for a Custom ID that your target uses. Ensure the value is passed in quotes. See the README for more details on this.',
        default='',
        metavar='REGEX',
        type=argCheckRegexCustomID
    )
    parser.add_argument(
        '-iq',
        '--ignore-querystring',
        action='store_true',
        help='Remove the query string (including URL fragments `#`) so output is unique paths only.',
    )
    parser.add_argument(
        '-lang',
        '--language',
        action='store_true',
        help='If passed, and there are multiple URLs with different language codes as a part of the path, only one version of the URL will be output. The codes are specified in the "LANGUAGE" section of "config.yml".',
    )
    parser.add_argument("-nb", "--no-banner", action="store_true", help="Hides the tool banner.")
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output.')
    args = parser.parse_args()

    try:
        # If no input was given, raise an error
        if sys.stdin.isatty():
            if args.input is None:
                writerr(colored('You need to provide an input with -i argument or through <stdin>.', 'red'))
                sys.exit()

        # Get the config settings from the config.yml file
        getConfig()
        
        # If input is not piped, show the banner, and if --verbose option was chosen show options and config values
        if sys.stdin.isatty():
            # Show banner unless requested to hide
            if not args.no_banner:
                showBanner()
            if verbose():
                showOptionsAndConfig()

        # Process the input given on -i (--input), or <stdin>
        processInput()

        # Output the saved urls with parameters
        processOutput()
        
    except Exception as e:
        writerr(colored('ERROR main 1: ' + str(e), 'red'))      
          
    finally: # Clean up
        urlmap = None
        patternsSeen = None
        patternsCustomID = None
        patternsGUID = None
        patternsInt = None
        patternsLang = None
           
if __name__ == '__main__':
    main()
    
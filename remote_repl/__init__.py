from sims4.commands import CheatOutput, Command, CommandType
from uuid import UUID

_bridged_ui = None
_bridged_ui_uuid = UUID('29e2dcda-7850-4a9f-80c2-f882600eadec')

@Command("remote_repl.launch", command_type=CommandType.Live)
def command_launch_remote_debugger(_connection=None):
    respond_to_player = CheatOutput(_connection)

    global _bridged_ui
    if _bridged_ui is not None:
        respond_to_player("My bridged UI is already open in PlumbBuddy.")
        _bridged_ui.focus()
        return

    try:
        from plumbbuddy_proxy.asynchronous import await_for, listen_for
        from plumbbuddy_proxy.api import gateway, PlumbBuddyNotConnectedError, PlayerDeniedRequestError, BridgedUiNotFoundError

        def initialize_bridged_ui(bridged_ui):
            global _bridged_ui
            _bridged_ui = bridged_ui

            @listen_for(bridged_ui.announcement)
            def handle_bridged_ui_announcement(announcement):
                if isinstance(announcement, dict): # is the announcement a structured object?
                    announcement_code = None
                    try:
                        announcement_code = announcement['code']
                    except KeyError:
                        pass
                    if announcement_code is not None and isinstance(announcement_code, str): # were we given Python code?
                        announcement_type = None
                        try:
                            announcement_type = announcement['type']
                        except KeyError:
                            pass
                        if announcement_type == 'exec': # have we been asked to just execute it?
                            try: # this might not work if Lump has a typo
                                exec_results_list = list()
                                exec_results_dict = dict()
                                exec(announcement_code, None, {
                                    '__EXEC_RESULTS_LIST__': exec_results_list,
                                    '__EXEC_RESULTS_DICT__': exec_results_dict
                                })
                                bridged_ui.send_data({ # oh sweet, it worked, let the bridged UI know
                                    'type': 'exec_result',
                                    'results_list': exec_results_list,
                                    'results_dict': exec_results_dict,
                                    'success': True
                                })
                            except Exception as ex:
                                bridged_ui.send_data({ # aww shit, better fess up
                                    'type': 'exec_result',
                                    'thrown': str(ex)
                                })
                        elif announcement_type == 'eval': # have we been asked to EVALUATE something?
                            try: # this might not work if Lump has a typo
                                bridged_ui.send_data({ # awesome, let's give Lumpinou what she's trying to see
                                    'type': 'eval_result',
                                    'eval_result': eval(announcement_code)
                                })
                            except Exception as ex:
                                bridged_ui.send_data({ # damn, fat-fingered something, madame
                                    'type': 'eval_result',
                                    'thrown': str(ex)
                                })
                        else:
                            bridged_ui.send_data({ # so, Python code but no specific instruction on what to do with it?
                                'type': 'unknown_type'
                            })
                    else:
                        bridged_ui.send_data({ # we can't do anything without Python code, so...
                            'type': 'no_code'
                        })
                else:
                    bridged_ui.send_data({ # what even... is this?
                        'type': 'unrecognized_announcement_type'
                    })
            
            @listen_for(bridged_ui.destroyed)
            def handle_bridged_ui_destroyed(_):
                global _bridged_ui
                _bridged_ui = None

        @await_for(gateway.look_up_bridged_ui(_bridged_ui_uuid))
        def look_up_bridged_ui_continuation(bridged_ui, fault):
            if bridged_ui:
                respond_to_player("My bridged UI is already open in PlumbBuddy.")
                initialize_bridged_ui(bridged_ui)
                bridged_ui.focus()
                return
            
            if isinstance(fault, PlumbBuddyNotConnectedError):
                respond_to_player("I can't display my bridged UI since you've shutdown PlumbBuddy! Start it back up and try again...")
                return
            
            if not isinstance(fault, BridgedUiNotFoundError):
                respond_to_player(f"I tried to look up a reference to my bridged UI and the look up failed for an unexpected reason: {str(fault)}")
                return
            
            #@await_for(gateway.request_bridged_ui(None, 'http://localhost:3000', _bridged_ui_uuid, 'Remote REPL', 'You typed the command in the game console to get me to make this request.', 'Remote REPL', 'tab-icon.png'))
            @await_for(gateway.request_bridged_ui(__file__, 'ui', _bridged_ui_uuid, 'Remote REPL', 'You typed the command in the game console to get me to make this request.', 'Remote REPL', 'tab-icon.png'))
            def request_bridged_ui_continuation(bridged_ui, fault):
                if bridged_ui:
                    respond_to_player("I've opened my bridged UI in PlumbBuddy.")
                    initialize_bridged_ui(bridged_ui)
                    return
                
                if isinstance(fault, PlumbBuddyNotConnectedError):
                    respond_to_player("I can't display my bridged UI since you've shutdown PlumbBuddy! Start it back up and try again...")
                    return

                if isinstance(fault, PlayerDeniedRequestError):
                    respond_to_player("Well, PlumbBuddy says you denied permission to display my bridged UI. Don't know why you asked...")
                    return
                
                respond_to_player(f"I tried to request a reference to my bridged UI and the request failed for an unexpected reason: {str(fault)}")

    except ModuleNotFoundError:
        respond_to_player("I couldn't find the PlumbBuddy Proxy, so... you may need to download and run PlumbBuddy from https://plumbbuddy.app -OR- you've turned off runtime integration in PlumbBuddy.")

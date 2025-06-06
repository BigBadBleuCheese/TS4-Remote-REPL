from sims4.commands import CheatOutput, Command, CommandType
from uuid import UUID

_bridged_ui = None
_bridged_ui_uuid = UUID('29e2dcda-7850-4a9f-80c2-f882600eadec')

@Command("remote_repl.launch", command_type=CommandType.Live)
def command_launch_remote_debugger(_connection=None):
    global _bridged_ui
    try:
        from plumbbuddy_proxy.api import gateway, BridgedUi
        if _bridged_ui is not None:
            _bridged_ui.focus()
            return
        # request the bridged UI
        eventual_bridged_ui = gateway.request_bridged_ui(__file__, 'ui', _bridged_ui_uuid, 'Remote REPL', 'You typed the command in the game console to get me to make this request.', 'Remote REPL')
        def bridged_ui_announcement(announcement):
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
                            _bridged_ui.send_data({ # oh sweet, it worked, let the bridged UI know
                                'type': 'exec_result',
                                'results_list': exec_results_list,
                                'results_dict': exec_results_dict,
                                'success': True
                            })
                        except Exception as ex:
                            _bridged_ui.send_data({ # aww shit, better fess up
                                'type': 'exec_result',
                                'thrown': str(ex)
                            })
                    elif announcement_type == 'eval': # have we been asked to EVALUATE something?
                        try: # this might not work if Lump has a typo
                            _bridged_ui.send_data({ # awesome, let's give Lumpinou what she's trying to see
                                'type': 'eval_result',
                                'eval_result': eval(announcement_code)
                            })
                        except Exception as ex:
                            _bridged_ui.send_data({ # damn, fat-fingered something, madame
                                'type': 'eval_result',
                                'thrown': str(ex)
                            })
                    else:
                        _bridged_ui.send_data({ # so, Python code but no specific instruction on what to do with it?
                            'type': 'unknown_type'
                        })
                else:
                    _bridged_ui.send_data({ # we can't do anything without Python code, so...
                        'type': 'no_code'
                    })
            else:
                _bridged_ui.send_data({ # what even... is this?
                    'type': 'unrecognized_announcement_type'
                })
        def bridged_ui_destroyed():
            # Lumpinou is done checking out the Python environment remotely, clean up our reference
            global _bridged_ui
            _bridged_ui = None
        def result_callback(bridged_ui: BridgedUi):
            # set our instance of the bridged UI reference
            global _bridged_ui
            _bridged_ui = bridged_ui
            # tell the reference we want to know when the bridged UI makes an announcement or is destroyed
            _bridged_ui.announcement.add_listener(bridged_ui_announcement)
            _bridged_ui.destroyed.add_listener(bridged_ui_destroyed)
        eventual_bridged_ui.then(result_callback) # tell the Eventual what to do when PB answers
    except ModuleNotFoundError:
        output = CheatOutput(_connection)
        output("I couldn't find the PlumbBuddy Proxy, so... you may need to download and run PlumbBuddy from https://plumbbuddy.app -OR- you've turned off runtime integration in PlumbBuddy.")

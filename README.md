Modes:

text normally - to use gemini api for reply
add '?' in front of your query - to use gemini api for reply but the reply falls to your DM instead of the group chat
command mode

Commands: <.....> - input

1)To CREATE a reminder
    syntax: !remind <date> <time> <message>
    example: in this format
    !remind 2025-03-05 12:01:10 Complete my project
    
2)To MODIFY a reminder
    syntax: !remind_modify <message_id> <new_date> <new_time> <new_message>
    example: in this format, message_id will be shown in chat as soon as a reminder is set
    !remind_modify 7cdfb296 2025-03-05 12:01:30 hi!
    
3)To DELETE a reminder
    syntax : !remind_delete <message_id>
    example: in this format
    !remind_delete d2519967
    
4)To CREATE a poll
    syntax: !poll "<message_to_be_appeared_for_poll>" <option_1> <option_2> ..... <option_10>
    the number of option has been capped to 10
    example: in this format
    !poll "Best number" 1 2 3 4 5 6 7 8 9 10

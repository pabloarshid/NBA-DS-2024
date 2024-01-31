from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder, playbyplayv3
import pandas as pd

#Mapping out all of the EventMsgActionTypes for EventMsgType 2
import re
import operator
from nba_api.stats.library.parameters import Season
from nba_api.stats.library.parameters import SeasonType

# get_teams returns a list of 30 dictionaries, each an NBA team.
nba_teams = teams.get_teams()
# print("Number of teams fetched: {}".format(len(nba_teams)))



pacers = [team for team in nba_teams if team["full_name"] == "Indiana Pacers"][0]
pacers_id = pacers['id']
# print(f'pacers_id: {pacers_id}')

gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=pacers_id,
                            season_nullable=Season.default,
                            season_type_nullable=SeasonType.regular)  

games_dict = gamefinder.get_normalized_dict()
games = games_dict['LeagueGameFinderResults']
game = games[5]
game_id = game['GAME_ID']
game_matchup = game['MATCHUP']

# print(f'Searching through {len(games)} game(s) for the game_id of {game_id} where {game_matchup}')

# print(games_dict)

#the following expression is specific to EventMsgType 1
p = re.compile('(\s{2}|\' )([\w+ ]*)')

#get the PlayByPlay data from the Pacers game_id
plays = playbyplayv3.PlayByPlayV3(game_id)
print(plays.get_data_frames())

#declare a few variables
description = ''
event_msg_action_types = {}

#loop over the play by play data
# print(plays[0])
# for play in plays:
#     if play['EVENTMSGTYPE'] == 1:
#         description = play['HOMEDESCRIPTION'] if play['HOMEDESCRIPTION'] is not None else play['VISITORDESCRIPTION']
#         if description is not None:
#             match = p.search(description)
#             if match:  # Check if the regex search found a match
#                 event_msg_action = re.sub(' ', '_', match.groups()[1].rstrip()).upper()
#                 # print(event_msg_action)
#                 event_msg_action_types[event_msg_action] = play['EVENTMSGACTIONTYPE']
            
# # #sort it all
# event_msg_action_types = sorted(event_msg_action_types.items(), key=operator.itemgetter(0))

# #output a class that we could plug into our code base
# for action in event_msg_action_types:
#     print(f'\t{action[0]} = {action[1]}')



# Process the plays and create a list of dictionaries for each play
# processed_plays = []
# for play in plays:
#     print(play)
#     # Determine the description of the event
#     description = play.get('HOMEDESCRIPTION') or play.get('VISITORDESCRIPTION') or play.get('NEUTRALDESCRIPTION') or 'No Description'

#     # Append to the list
#     processed_plays.append({
#         'EVENTNUM': play['EVENTNUM'],
#         'PERIOD': play['PERIOD'],
#         'PCTIMESTRING': play['PCTIMESTRING'],
#         'DESCRIPTION': description,
#         'SCORE': play['SCORE']
#     })

# Display the first few entries of the processed plays
# for play in processed_plays[:5]:  # Print first 5 plays
    # print(play)



# #declare a few variables
# description = ''
# event_msg_action_types = {}

# #loop over the play by play data
# #do a bit of findall(regex) and a little character magic: underscores and upper case
# #we're using a findall here as we have to deal with the extra word MISS at the beginning of the text.
# #that extra text means we'll have multiple matches for our regex.
# for play in plays:
#     if play['EVENTMSGTYPE'] == 2:
#         match = list()
#         if play['HOMEDESCRIPTION'] is not None: 
#             match = p.findall(play['HOMEDESCRIPTION'])
        
#         if not match:
#             match = p.findall(play['VISITORDESCRIPTION'])

#         event_msg_action = re.sub(' ', '_', match[0][1]).upper()
#         event_msg_action_types[event_msg_action] = play['EVENTMSGACTIONTYPE']
        
#        # if play['EVENTMSGACTIONTYPE']
        
# event_msg_action_types = sorted(event_msg_action_types.items(), key=operator.itemgetter(0))

# for action in event_msg_action_types:
#     print(f'\t{action[0]} = {action[1]}')
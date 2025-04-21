# %%
import random
import pandas as pd
from collections import defaultdict
import deuces
import itertools
from math import floor

# %%
class Card:
    def __init__(self, rank:str, suit:str):
        self.rank = rank
        self.suit = suit

    # def __repr__(self):
    #     return str(self.rank+self.suit)
        
    @staticmethod
    def as_str(card):
        return card.rank+card.suit
    
    @staticmethod
    def as_str_list(card_list, keep:str='both'):
        if keep == 'both':
            return [card.rank+card.suit for card in card_list]
        elif keep == 'rank':
            return [card.rank for card in card_list]
        elif keep == 'suit':
            return [card.suit for card in card_list]
    
    @staticmethod
    def convert_deuces_ints_to_strs(card_list):
        return [deuces.Card.int_to_str(card) for card in card_list]

    @staticmethod
    def convert_card_strs_to_deuces(card_list):
        return [deuces.Card.new(card) for card in card_list]
    
    @staticmethod
    def get_ranks(card_list):
        rank_dict = defaultdict(int)
        rank_class = ''
        relevant_cards = []
        for card in card_list: rank_dict[card[0]] += 1
        four_of_a_kind_idx = [key for key, val in rank_dict.items() if val == 4]
        three_of_a_kind_idx = [key for key, val in rank_dict.items() if val == 3]
        pairs_idx = [key for key, val in rank_dict.items() if val == 2]
        if len(four_of_a_kind_idx) == 1: rank_class = 'Four of a Kind'
        elif len(three_of_a_kind_idx) == 1: rank_class = 'Three of a Kind'
        elif len(pairs_idx) == 2: rank_class = 'Two Pair'
        elif len(pairs_idx) == 1: rank_class = 'Pair'
        else: rank_class = 'High Card'
        if rank_class == 'Four of a Kind':
            relevant_cards = [card for card in card_list if card[0] == four_of_a_kind_idx[0]]
        elif rank_class == 'Three of a Kind':
            relevant_cards = [card for card in card_list if card[0] == three_of_a_kind_idx[0]]
        elif rank_class == 'Two Pair':
            relevant_cards = [card for card in card_list if card[0] in pairs_idx]
        elif rank_class == 'Pair':
            relevant_cards = [card for card in card_list if card[0] in pairs_idx]
        else:
            for rank in list(Deck_Manager.rank_values.keys()):
                relevant_cards = next((card for card in card_list if rank == card[0]), None)
                if relevant_cards != None: 
                    relevant_cards = [relevant_cards]
                    break
        return [rank_class, relevant_cards]
    
class Run_Manager:
    ante_vals = [300, 800, 2000, 5000, 11000, 20000, 35000, 50000]
    ante_endless_vals = [1.1e+5, 5.6e+5, 7.2e+6, 3e+8, 4.7e+10, 2.9e+13, 7.7e+16, 8.6e+20]
    ante_vals += ante_endless_vals
    blind_mult = [1, 1.5, 2]
    blind_values = [int(round[0]*round[1]) for round in list(itertools.product(ante_vals,blind_mult))]
    attempts = 4

    def __init__(self):
        self.run_analytics = defaultdict(float)
        self.round_score = 0
        self.discards = 0
        self.output_df = pd.DataFrame()
         
    
    def blind_tracker(self, deck_m):
        for round,blind in enumerate(self.blind_values):
            #print("--- Blind Goal: ",blind," ---")
            #print(" *** Round " , round+1, "*** ")
            self.round_score = 0
            self.discards = 0
            for attempt in range(self.attempts):
                run_dict = deck_m.draw_cards_and_get_best_hand()
                #print(run_dict)
                self.round_score += run_dict['score']
                self.discards += run_dict['discards_used']
                self.run_analytics['Total Run Score'] += run_dict['score']
                self.run_analytics['Total Discards Used'] += run_dict['discards_used']
                self.run_analytics[(run_dict['hand_type'] + ' Count')] += 1
                self.run_analytics['Total Cards Played'] += run_dict['cards_played']

                if run_dict['score'] > self.run_analytics['Best Hand Score']:
                    self.run_analytics['Best Hand Score'] = run_dict['score']
                    self.run_analytics['Hand played for Best Hand Score'] = run_dict['hand_type']

                #print("Current Round Score:", self.round_score)
                if self.round_score >= blind:
                    #print("**** You've reached the Blind Goal ****\n")
                    #print("Total Run Score:", self.run_analytics['Total Run Score'],"\n")
                    break
            deck_m.shuffle_deck()
            if self.round_score < blind:
                #print("**** You did not meet the Goal for the Blind ****")
                self.run_analytics['Total Run Score'] = self.run_analytics['Total Run Score']
                self.run_analytics['Total Discards Used'] = self.run_analytics['Total Discards Used']
                self.run_analytics['Rounds Won'] = round
                self.run_analytics['Rounds Played'] = round + 1
                self.run_analytics['Antes Won'] = floor(self.run_analytics['Rounds Won']/3)
                #print("Total Run Score:", self.run_analytics['Total Run Score'],"\n")
                break
        self.calculate_store_clean()

    
    
    def calculate_store_clean(self):
        self.run_analytics['Run Average Score'] = round(self.run_analytics['Total Run Score']/self.run_analytics['Rounds Played'],1) if self.run_analytics['Rounds Played']!=0 else 0
        self.run_analytics['Average Discards'] = round(self.run_analytics['Total Discards Used']/self.run_analytics['Rounds Played'],1) if self.run_analytics['Rounds Played']!=0 else 0
        # print(dict(self.run_analytics))
        self.output_df = pd.concat([self.output_df, pd.DataFrame(self.run_analytics,index=[0])])
        self.run_analytics.clear()

    def batch_run(self,runs,deck_m):
        for run in range(runs):
            self.blind_tracker(deck_m)
        self.output_df = self.output_df.fillna(0)
        count_cols = sorted([col for col in self.output_df.columns if ' Count' in col])
        other_cols = [col for col in self.output_df.columns if ' Count' not in col]
        self.output_df = self.output_df[other_cols + count_cols]
        self.output_df.to_csv('run_analytics_output.csv')
        self.output_df = pd.DataFrame()
        


class Deck_Manager:
    evaluator = deuces.Evaluator()
    suits = ['d', 'h', 'c', 's']
    rank_values = {
        'A': 11,
        'K': 10,
        'Q': 10,
        'J': 10,
        'T': 10,
        '9': 9,
        '8': 8,
        '7': 7,
        '6': 6,
        '5': 5,
        '4': 4,
        '3': 3,
        '2': 2
    }
    hand_values = {
        'Straight Flush': (100, 8),
        'Four of a Kind': (60, 7),
        'Full House': (40, 4),
        'Flush': (35, 4),
        'Straight': (30, 4),
        'Three of a Kind': (30, 3),
        'Two Pair': (20, 2),
        'Pair': (10, 2),
        'High Card': (5, 1),
    }
    discards = 3

    def __init__(self):
        self.deck = []
        self.hand_in_play = []
        self.discards_used = 0
        self.prev_discards_used = 0
        for suit in self.suits:
            for rank, value, in self.rank_values.items():
                self.deck.append(Card(rank, suit))
        self.shuffle_deck()
        self.first_hand_dealt = False

    def show_deck(self):
        if len(self.deck) == 0: print('No cards in deck!')
        else: 
            for card in self.deck:
                card.show_card()
    
    def shuffle_deck(self):
        random.shuffle(self.deck)
        self.deck_queue = (card for card in self.deck)
        self.first_hand_dealt = False
        self.hand_in_play = []
        self.discards_used = 0
        self.prev_discards_used = 0
    
    def draw_card(self):
        try:
            return next(self.deck_queue)
        except StopIteration:
            return None
    
    def draw_cards(self, n:int=8) -> list[str]:
        """
        Return list of Card objects until Card generator empty
        """
        card_list = []
        if self.first_hand_dealt == False: 
            cards_to_deal = 8
            self.first_hand_dealt = True
        else: 
            cards_to_deal = n
        for i in range(cards_to_deal):
            new_card = self.draw_card()
            if new_card != None:
                card_list.append(new_card)
            else:
                break
        card_list_str = Card.as_str_list(card_list)
        self.hand_in_play = card_list_str
        return card_list_str
    
    def n_card_eval(self, cards_as_str:list[str]) -> list:
        cards_as_int = Card.convert_card_strs_to_deuces(cards_as_str)
        minimum = deuces.lookup.LookupTable.MAX_HIGH_CARD # 7462
        minimum_combo = []
        all5cardcombos = itertools.combinations(cards_as_int, 5)
        for combo in all5cardcombos:
            score = self.evaluator._five(combo)
            if score < minimum:
                minimum = score
                minimum_combo = Card.convert_deuces_ints_to_strs(combo)
        return [minimum, minimum_combo]
    
    def get_best_hand(self, cards_as_str:list[str]) -> list:
        if len(cards_as_str) >= 5:
            best_hand_type_int, best_cards = self.n_card_eval(cards_as_str)
            best_hand_type = self.evaluator.class_to_string(self.evaluator.get_rank_class(best_hand_type_int))
            if best_hand_type in ['Straight Flush', 'Full House', 'Flush', 'Straight']:
                return [best_hand_type, best_cards]
            else:
                best_hand_type, best_cards = Card.get_ranks(cards_as_str)
                return [best_hand_type, best_cards]
        else:
            best_hand_type, best_cards = Card.get_ranks(cards_as_str)
            return [best_hand_type, best_cards]
        
    def discard_and_draw_cards(self):
        self.hand_in_play.sort(key=lambda card:list(Deck_Manager.rank_values.keys()).index(card[0]))
        lowest_cards = self.hand_in_play[3:] # lowest 5 cards
        # print(f'Lowest: {lowest_cards} from {self.hand_in_play}')
        self.hand_in_play = [card for card in self.hand_in_play if card not in lowest_cards]
        self.hand_in_play += self.draw_cards(8-len(self.hand_in_play))
        return self.get_best_hand(self.hand_in_play)

    def draw_cards_and_get_best_hand(self) -> list:
        cards_played = 0
        # print(f'{self.hand_in_play} - current hand')
        if not self.first_hand_dealt:
            self.hand_in_play += self.draw_cards(8-len(self.hand_in_play))
        best_hand_type, best_cards = self.get_best_hand(self.hand_in_play)
        while(self.discards_used < self.discards):
            if best_hand_type in ['Pair', 'High Card']:
                # print(f'Discard {self.discards_used+1}')
                best_hand_type, best_cards = self.discard_and_draw_cards()
                self.discards_used += 1
            else:
                break
        # print(f'{best_hand_type}: {best_cards}')
        self.hand_in_play = [card for card in self.hand_in_play if card not in best_cards]
        # print(f'{self.hand_in_play} - cards left over')
        self.hand_in_play += self.draw_cards(8-len(self.hand_in_play))
        score = list(self.hand_values[best_hand_type])
        if not best_cards: return 0
        for card in best_cards: 
            score[0] += self.rank_values[card[0]]
            cards_played += 1
            # if card[1] == 'd': score[1] += 3 #greedy joker
            # if card[0] == 'K': score[1] *= 1.5 #baron
            # if card[0] in ['A','2','3','5','8']: score[1] += 8 #fibonnaci
            # if card[0] in ['T','4']: 
            #     score[0] += 10 
            #     score[1] += 4 #walkie talkie
            # if card[0] in ['K','Q']: score[1] *= 2 #triboulet
        # if best_hand_type in ['Two Pair', 'Full House']: score[1] += 10 #mad joker
        # if best_hand_type in ['Two Pair', 'Full House']: score[0] += 80 #clever joker
        # score[1] += random.randint(0,23) #misprint joker

        # print(f'{score[0]*score[1]} from {score}')
        data_dict = {
            'score': score[0]*score[1],
            'hand_type': best_hand_type,
            'cards_played': cards_played,
            'discards_used': self.discards_used-self.prev_discards_used
        }
        self.prev_discards_used = self.discards_used
        return data_dict

# %%

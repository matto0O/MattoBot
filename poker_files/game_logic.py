from discord.ext import commands
import asyncio
from .cards import Deck, Hand
from .players import *


class Pot:
    def __init__(self, in_pot=[], total=0):
        self.contributions = dict()
        for player in in_pot:
            self.contributions[player] = 0
        self.total = total

    def chip_in(self, player, amount):
        self.contributions[player] += amount
        self.total += amount

    def next_round(self):
        for key in self.contributions.keys():
            self.contributions[key] = 0

    def folded(self, player):
        self.contributions.pop(player)
        player.status=PlayerStatus.FOLDED

    def to_call(self, player):
        return max(self.contributions.values()) - self.contributions[player]
        

class Game:
    def __init__(self, players, stack=5000, small_blind=50, big_blind=100):
        self.deck = Deck()
        self.temp_deck = self.deck
        self.temp_deck.shuffle()
        self.player_data = [Player(player[0], player[1][1], stack) for player in players]
        self.pot = Pot(self.player_data)
        self.dealer_index = 0
        self.turn_index = 3 % len(self.player_data)
        self.sb = small_blind
        self.bb = big_blind
        self.table_cards = []
        self.turn_queue = []

    def reset(self):
        self.pot = Pot(self.player_data)
        self.move_dealer()
        for player in self.player_data:
            player.reset_status()
        i = len(self.player_data) - 1
        while self.player_data[self.dealer_index].status == PlayerStatus.BROKE:
            self.move_dealer()
            i -= 1
            if i == 0: return False
        self.temp_deck = self.deck
        self.temp_deck.shuffle()
        return True

    async def announce(self, text):
        for player in self.player_data:
            await player.channel.send(text)

    async def game_state_announce(self):
        message = ''
        for i, player in enumerate(self.player_data):
            flag = ''
            if i==self.dealer_index:
                flag = 'D '
            if i==(self.dealer_index + 2) % len(self.player_data):
                flag += 'BB'
            elif i==(self.dealer_index + 1) % len(self.player_data):
                flag += 'SB'
            if i==self.turn_index:
                message += f'    -->'
            message += f'{flag} {player} {player.stack} '
            try:
                message += str(self.pot.contributions[player])
            except KeyError:
                message += 'FOLDED'
            finally:
                message += '\n'
        
        await self.announce(message)
            
    def change_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.pot.contributions)
        i = 0
        while self.player_data[self.turn_index].status != PlayerStatus.PLAYING:
            self.turn_index = (self.turn_index + 1) % len(self.pot.contributions)
            if i == len(self.player_data):
                return False
            else: i += 1
        return True

    async def deal(self):
        order_range = range(self.dealer_index + 1, self.dealer_index + len(self.player_data) + 1)
        for _ in range(2):
            for i in order_range:
                player = self.player_data[i%len(self.player_data)]
                if player.status != PlayerStatus.BROKE:
                    player.hand.append(self.temp_deck.get_card())
        for player in (self.player_data):
            await player.channel.send(files=[card.file for card in player.hand])

    async def flop(self):
        self.temp_deck.get_card()
        flop = [self.temp_deck.get_card() for _ in range(3)]
        self.table_cards = flop
        for player in self.player_data:
            await player.channel.send(files=[card.file for card in flop])

    async def turn_river(self):
        self.temp_deck.get_card()
        card = self.temp_deck.get_card()
        self.table_cards.append(card)
        for player in self.player_data:
            await player.channel.send(file=card.file)

    def move_dealer(self):
        self.dealer_index = (self.dealer_index + 1) % len(self.player_data)
        self.turn_index = (self.dealer_index + 3) % len(self.player_data)

    async def get_available_moves(self, player: Player):
        moves = ["!fold", "!all-in"]
        message = "Available moves:\n > fold\n"
        to_call = self.pot.to_call(player)
        if to_call == 0:
            moves.append("!check")
            message += " > check\n"
            moves.append("!raise")
            message += f" > raise\n"
        elif to_call < player.stack:
            moves.append("!call")
            moves.append("!raise")
            message += f" > call ({to_call})\n"
            message += f" > raise\n"
        elif to_call == player.stack:
            moves.append("!call")
            message += f" > call ({to_call})\n"
        message += f" > all-in ({player.stack})"

        await player.channel.send(message)
        return moves

    async def show_hand(self, player):
        await player.channel.send(content=f"{player}'s hand:\n", files=[card.file for card in player.hand])

    async def betting_phase(self, client, starting_index = 1):
        async def over_check():
            if len(self.turn_queue) == 1:
                self.turn_queue[0].stack += self.pot.total
                for player in self.player_data:
                    player.reset_status()
                self.turn_queue = list(filter(lambda x: x.status==PlayerStatus.PLAYING,self.player_data))
                await self.announce(f"{self.turn_queue[0]} won the {self.pot.total} pot")
                return True
            return False
        
        while len(self.turn_queue) > 1:
            order_range = range(self.dealer_index + starting_index, self.dealer_index + len(self.turn_queue) + starting_index)
            self.turn_queue = list(filter(lambda x: x.status==PlayerStatus.PLAYING,self.player_data))
            for i in order_range:
                player = self.turn_queue[i%len(self.turn_queue)]
                await self.game_state_announce()
                moves = await self.get_available_moves(player)

                def check(m):
                    if not player.player==m.author:
                        print("false1", player.player, m.author)
                        return False
                    if m.channel != player.channel:
                        print("false2", player.channel, m.channel)
                        return False
                    if not m.content.startswith("!"):
                        print("false3", m.content)
                        return False
                    if any(action in m.content for action in moves):
                        return True
                    return False

                try:
                    message = await client.wait_for('message', timeout=60, check=check)
                    await self.announce(f"{self.player_data[self.turn_index]}'s decision - {message.content[1:]}")
                except asyncio.TimeoutError:
                    await self.announce(f"{self.player_data[self.turn_index]}'s decision - fold")
                    player.folded()
                    self.pot.folded(player)
                    self.turn_queue.remove(player)
                if await over_check(): return True
                self.change_turn()
            
            if len(set(self.pot.contributions.values())) == 1: break

        return False

    async def play(self, client: commands.Bot):
        self.turn_queue = list(filter(lambda x: x.status==PlayerStatus.PLAYING,self.player_data))
        
        while len(self.turn_queue) > 1 and self.reset():
            await self.deal()
            self.pot = Pot(self.turn_queue, self.sb + self.bb)
            sb = list(self.pot.contributions.keys())[(self.dealer_index + 1) % len(self.pot.contributions)]
            bb = list(self.pot.contributions.keys())[(self.dealer_index + 2) % len(self.pot.contributions)]

            sb.stack -= self.sb
            self.pot.contributions[sb] = self.sb
            bb.stack -= self.bb
            self.pot.contributions[bb] = self.bb

            if not await self.betting_phase(client, 3):

                await self.flop()
                if not await self.betting_phase(client):

                    await self.turn_river()
                    if not await self.betting_phase(client):

                        await self.turn_river()
                        if not await self.betting_phase(client):
                            hands = []
                            for player in list(self.pot.contributions.keys()):
                               hands.append(Hand(self.table_cards, player))
                            hands.sort(reverse=True)
                            winners = [hands[0]]
                            for i in range(1, len(hands)):
                                if hands[0] == hands[i]:
                                    winners.append(hands[i])
                                else: break
                            won_amount = int(self.pot.total / len(winners))     # tip for the dealer :DDD
                            for hand in winners:
                                hand.player.stack += won_amount
                                await self.announce(f"{hand.player} won {won_amount} of the pot")
                                await self.show_hand(hand.player)
                            

        await self.announce(f"{self.turn_queue[0]} is the winner!")

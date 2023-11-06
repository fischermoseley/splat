So uh, what's next?
- (DONE, it's actually pretty nice. or nice enough) - See if the builtin build system is any good
- (DONE, will do HITL when the uart interface is online) - IO core tests need to be pytestified

- IO core needs external clock
- Probably worth porting the uart interface next so we can do some proper system integration, build proper bitstreams without hacking this time
    - begs the question of just importing verilog vs porting to amaranth
    - can we simulate if we load a module externally? probably worth checking
    - would also be neat to try and port to amaranth just to get a feel for the language

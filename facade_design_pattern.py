# Wrapper for main context handler if you have lot of stuff going on
"""
In our case notificationsytem has being doing lot of things
it building the chain
initializind the observers attaching those
initializing the factory
initializing the strategy
everything

such class when directly exposed to client can be problematic we should hide all this logic using Facade design pattern
"""
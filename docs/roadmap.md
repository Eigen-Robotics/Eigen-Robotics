# Ark Monster roadmap

1. [x] fix mac/x86_64 installation
2. [] fix opencv on mac/arm64
3. [] prepare the repo into a state where someone not faimiliar with UV will be
able to go ahead and test the "dev" side of things, from zero to hero, to get a
gauge on the onboarding experience
    - this should instruct them to do some minimal changes on top of the existing
    things, which includes getting setup with the environment

## Ark Modularity

1. [x] We want to modularize robots|sensors and their corresponding driver, we will need a registartion system such that the defaults are automatically included and users can register their custom implementations
2. [] We will need sets of dependencies for each default registration such that we can check if those dependencies are present
3. [] Users should be able to list what registered components are present and which of them are runable given the current instalation
4. [] Make the components instantiable and executable with a config argument
5. [] Integrate with Ark Graph (@Sarthak)

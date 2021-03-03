state_update_blocks = [
    {
        'policies': {
            'example_policy': lambda params, *kwargs: {'example_signal': 1} 
        },
        'variables': {
            'example_state': lambda params, *kwargs: ('example_state', 1)
        }
    }
]

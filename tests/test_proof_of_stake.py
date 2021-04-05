from model.parts.proof_of_stake import approximate_inclusion_distance


def test_inclusion_distance():
    number_of_validators = 1000
    validators_offline_pct = 0.0
    inclusion_distance = approximate_inclusion_distance(number_of_validators, validators_offline_pct)
    assert inclusion_distance == 1

    validators_offline_pct = 0.5
    inclusion_distance = approximate_inclusion_distance(number_of_validators, validators_offline_pct)
    assert 0 < inclusion_distance <= 1

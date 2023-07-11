import { Args, Mutation, Query, Resolver, Subscription } from '@nestjs/graphql';
import { User } from './user.entity';
import { UserService } from './user.service';
import { UserInput, UserOutput } from './user.dto';
import { PubSub } from 'graphql-subscriptions';

const pubSub = new PubSub();

@Resolver(() => UserOutput)
export class UserResolver {
	constructor(private readonly dataService: UserService) {}

	@Mutation(() => UserOutput)
	async addUser(@Args('newUser') newUser: UserInput): Promise<UserOutput> {
		const data = await this.dataService.createUser(
			User.fromUserInput(newUser),
		);
		pubSub.publish('dataAdded', { dataAdded: data });
		return UserOutput.fromUser(data);
	}

	@Mutation(() => UserOutput)
	async checkUser(@Args('inputUser') inputUser: UserInput): Promise<UserOutput> {
		const data = await this.dataService.findOneBy({username: inputUser.username})
	}

	@Subscription(() => User)
	dataAdded() {
		return pubSub.asyncIterator('dataAdded');
	}
}

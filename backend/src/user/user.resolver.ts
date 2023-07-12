import { Args, Mutation, Query, Resolver, Subscription } from '@nestjs/graphql';
import { User } from './user.entity';
import { UserService } from './user.service';
import { LoginInput, UserInput, UserOutput } from './user.dto';
import { PubSub } from 'graphql-subscriptions';
import { Md5 } from 'ts-md5';
import { Session } from './session.entity';
import { JwtService } from '@nestjs/jwt';

const pubSub = new PubSub();

@Resolver(() => UserOutput)
export class UserResolver {
	constructor(private readonly userService: UserService, private jwtService: JwtService) { }

	@Mutation(() => UserOutput)
	async addUser(@Args('newUser') newUser: UserInput): Promise<UserOutput | Error> {
		const data = await this.userService.createUser(
			User.fromUserInput(newUser),
		);
		pubSub.publish('dataAdded', { dataAdded: data });
		return this.LogIn(LoginInput.fromUserInput(newUser))
	}

	@Mutation(() => UserOutput)
	async LogIn(@Args('loginUser') loginUser: LoginInput): Promise<UserOutput | Error> {
		const user = await this.userService.findOneBy({ username: loginUser.username, hashedPassword: Md5.hashStr(loginUser.password) });
		if (user instanceof User) {
			const token = await this.jwtService.signAsync({ id: user.id, username: user.username, birthday: user.birthDay })
			const session = new Session(token, user);
			await this.userService.createSession(session);
			return UserOutput.fromUser(user, token)
		}
		return Error('Incorrect username or password.')
	}

	@Mutation(() => UserOutput)
	async LogOut(@Args('logoutUser') username: string, @Args('token') token: string) {
		const user = await this.userService.findOneBy({ username: username });
		if (user instanceof User) {
			const session = await this.userService.findSession({ user: user, token: token });
			if (session) {
				this.userService.removeSession(session)
			}
		}
		return Error('User already logged out.')
	}

	@Mutation(() => UserOutput)
	async checkToken(@Args('token') token: string): Promise<UserOutput | Error> {
		const session = await this.userService.findSession({ token: token });
		if (session) {
			const user = await this.userService.findOneBy({ id: session.id });
			if (user instanceof User) {
				return UserOutput.fromUser(user, token)
			}
		}
		return Error('Invalid token')
	}

	@Subscription(() => User)
	dataAdded() {
		return pubSub.asyncIterator('dataAdded');
	}
}

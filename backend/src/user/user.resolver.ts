import { Args, Mutation, Resolver, Subscription } from '@nestjs/graphql';
import { User } from './user.entity';
import { UserService } from './user.service';
import { LoginInput, UserInput, UserOutput } from './user.dto';
import { PubSub } from 'graphql-subscriptions';
import { Md5 } from 'ts-md5';
import { Session } from './session.entity';
import { TokenExpiredError } from 'jsonwebtoken';

const pubSub = new PubSub();

@Resolver(() => UserOutput)
export class UserResolver {
	constructor(private readonly service: UserService) { }

	@Mutation(() => UserOutput)
	async addUser(@Args('newUser') newUser: UserInput): Promise<UserOutput | Error> {
		const data = await this.service.createUser(
			User.fromUserInput(newUser),
		);
		pubSub.publish('dataAdded', { dataAdded: data });
		return this.LogIn(LoginInput.fromUserInput(newUser))
	}

	@Mutation(() => UserOutput)
	async LogIn(@Args('loginUser') loginUser: LoginInput): Promise<UserOutput | Error> {
		const user = await this.service.findOneBy({ username: loginUser.username, hashedPassword: Md5.hashStr(loginUser.password) });
		if (user instanceof User) {
			const token = this.service.createToken(user)
			const session = new Session(token, user);
			await this.service.createSession(session);
			return UserOutput.fromUser(user, token)
		}
		return Error('Incorrect username or password.')
	}

	@Mutation(() => String)
	async LogOut(@Args('username') username: string, @Args('token') token: string) {
		const user = await this.service.findOneBy({ username: username });
		if (user instanceof User) {
			const session = await this.service.findSession({ user: user, token: token });
			if (session) {
				this.service.removeSession(session)
				return 'Logged out'
			}
		}
		return Error('User already logged out.')
	}

	@Mutation(() => UserOutput)
	async checkToken(@Args('token') token: string): Promise<UserOutput | Error> {
		const session = await this.service.findSession({ token: token });
		if (session) {
			const user = await this.service.findOneBy({ id: session.user.id });
			if (user instanceof User) {
				try {
					this.service.checkToken(token);
				} catch (err) {
					if (err instanceof TokenExpiredError) {
						this.service.removeSession(session)
						const token = this.service.createToken(user);
						await this.service.createSession(new Session(token, user));
					} else {
						return Error('Error verifying token:' + err);
					}
				}
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

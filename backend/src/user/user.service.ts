import { FindOptionsWhere, Repository } from 'typeorm';
import { User } from './user.entity';
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Session } from './session.entity';
import { JwtService } from '@nestjs/jwt';

@Injectable()
export class UserService {
	constructor(
		@InjectRepository(User)
		private dataSource: Repository<User>,
		@InjectRepository(Session)
		private sessionSource: Repository<Session>,
		private jwtService: JwtService
	) { }

	// Section: User
	async findUserOneBy(args: FindOptionsWhere<User>): Promise<User | Error> {
		return await this.dataSource.manager.findOneBy(User, args) ?? Error('User not found');
	}

	async createUser(createUserInput: User): Promise<User> {
		const data = this.dataSource.manager.create(User, createUserInput);
		return await this.dataSource.manager.save(User, data);
	}

	async removeUser(arg: FindOptionsWhere<User>): Promise<void> {
		const data = await this.findUserOneBy(arg);
		await this.dataSource.manager.remove(User, data);
	}

	// Section: Session
	async createSession(newSession: Session) {
		this.sessionSource.manager.save(Session, newSession)
	}

	async findSession(args: FindOptionsWhere<Session>) {
		return await this.sessionSource.manager.findOneBy(Session, args);
	}

	async removeSession(session: Session) {
		this.sessionSource.manager.remove(Session, session)
	}

	// Section: Token
	createToken(user: User) {
		return this.jwtService.sign({ create: Date.now(), username: user.username, userStr: user.givenName + user.familyName + user.gender + user.birthDay, id: user.id });
	}

	checkToken(token: any) {
		return this.jwtService.verify(token);
	}
}

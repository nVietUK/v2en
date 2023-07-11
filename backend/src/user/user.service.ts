import { FindOptionsWhere, Repository } from 'typeorm';
import { User } from './user.entity';
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Session } from './session.entity';

@Injectable()
export class UserService {
	constructor(
		@InjectRepository(User)
		private dataSource: Repository<User>,
		@InjectRepository(Session)
		private sessionSource: Repository<Session>
	) { }

	async findOneBy(args: FindOptionsWhere<User>): Promise<User> {
		return await this.dataSource.manager.findOneBy(User, args) ?? new User();
	}

	async createUser(createUserInput: User): Promise<User> {
		const data = this.dataSource.manager.create(User, createUserInput);
		return await this.dataSource.manager.save(User, data);
	}

	async removeUser(arg: FindOptionsWhere<User>): Promise<void> {
		const data = await this.findOneBy(arg);
		await this.dataSource.manager.remove(User, data);
	}

	async createSession(newSession: Session) {
		this.sessionSource.manager.save(Session, newSession)
	}

	async findSession(args: FindOptionsWhere<Session>) {
		return await this.sessionSource.manager.findOneBy(Session, args);
	}

	async removeSession(session: Session) {
		this.sessionSource.manager.remove(Session, session)
	}
}

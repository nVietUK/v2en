import { FindOptionsWhere, Repository } from 'typeorm';
import { User } from './user.entity';
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';

@Injectable()
export class UserService {
	constructor(
		@InjectRepository(User)
		private dataSource: Repository<User>,
	) {}

	async findOneBy(args: FindOptionsWhere<User>): Promise<User | null> {
		return await this.dataSource.manager.findOneBy(User, args);
	}

	async createUser(createUserInput: User): Promise<User> {
		const data = this.dataSource.manager.create(User, createUserInput);
		return await this.dataSource.manager.save(User, data);
	}

	async removeUser(arg: FindOptionsWhere<User>): Promise<void> {
		const data = await this.findOneBy(arg);
		await this.dataSource.manager.remove(User, data);
	}
}